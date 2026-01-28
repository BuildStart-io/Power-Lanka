const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
const express = require('express');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
app.use(express.json());

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const PORT = process.env.PORT || 4000;

// Simple Logger
const logger = {
    info: (msg, ...args) => console.log(`[${new Date().toISOString()}] [INFO] ${msg}`, ...args),
    warn: (msg, ...args) => console.warn(`[${new Date().toISOString()}] [WARN] ${msg}`, ...args),
    error: (msg, ...args) => console.error(`[${new Date().toISOString()}] [ERROR] ${msg}`, ...args),
    debug: (msg, ...args) => console.log(`[${new Date().toISOString()}] [DEBUG] ${msg}`, ...args)
};

// Initialize WhatsApp Client
const client = new Client({
    authStrategy: new LocalAuth(),
  // change to let Puppeteer use its bundled Chromium
puppeteer: {
    headless: true,
    args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
    ]
}
});

// Generate QR Code
client.on('qr', (qr) => {
    logger.info('QR RECEIVED', qr);
    qrcode.generate(qr, { small: true });
    logger.info('Please scan the QR code with your WhatsApp to authenticate.');
});

// Client Ready
client.on('ready', async () => {
    logger.info('WhatsApp Client is ready!');
    // Set presence to online
    try {
        await client.sendPresenceAvailable();
        logger.info('Presence set to online');
    } catch (e) {
        logger.error('Failed to set presence:', e.message);
    }
});

// Authentication Failure
client.on('auth_failure', msg => {
    logger.error('AUTHENTICATION FAILURE', msg);
});

// Track processed messages to avoid duplicates
const processedMessages = new Set();

// Extract phone number helper
function extractPhoneNumber(waId) {
    return waId
        .replace("@c.us", "")
        .replace("@s.whatsapp.net", "")
        .replace("@newsletter", "");
}

// Handle incoming messages
async function handleMessage(msg) {
    try {
        // Deduplicate: check if we already processed this message
        const messageId = msg.id._serialized || msg.id;
        if (processedMessages.has(messageId)) {
            return;
        }

        // Skip messages from ourselves
        if (msg.fromMe) {
            return;
        }

        // Filter: skip groups, status, broadcasts
        if (msg.isGroupMsg || msg.isStatus || msg.broadcast) {
            return;
        }

        // Ignore messages from status@broadcast (double check)
        if (msg.from === 'status@broadcast') return;

        logger.info(`Received message from ${msg.from}: ${msg.body}`);

        // Mark as processed
        processedMessages.add(messageId);
        // Clean up old entries (keep last 100)
        if (processedMessages.size > 100) {
            const firstKey = processedMessages.values().next().value;
            processedMessages.delete(firstKey);
        }

        // Extract phone number
        const phoneNumber = extractPhoneNumber(msg.from);

        logger.debug(`Processing message from ${phoneNumber}`);

        // Get chat and show typing indicator
        const chat = await msg.getChat();

        // Try to send blue ticks (may fail due to WhatsApp API changes)
        try {
            await chat.sendSeen();
            logger.debug('Blue ticks sent');
        } catch (seenError) {
            logger.warn('sendSeen failed (non-critical):', seenError.message);
        }

        await chat.sendStateTyping();
        logger.debug('Typing indicator shown');

        const response = await axios.post(`${BACKEND_URL}/whatsapp/message`, {
            phone_number: phoneNumber,
            message: msg.body
        });

        logger.debug('Backend response received');

        if (response.data && response.data.response) {
            // Clear typing indicator
            try {
                logger.debug('Clearing typing state');
                await chat.clearState();

                // Check if there's a category image to send
                if (response.data.category_image) {
                    const imagePath = path.join(
                        __dirname,
                        '../backend/media',
                        response.data.category_image
                    );

                    logger.debug('Category image path:', imagePath);

                    if (fs.existsSync(imagePath)) {
                        try {
                            logger.debug('Sending image with caption');
                            const media = MessageMedia.fromFilePath(imagePath);
                            await chat.sendMessage(media, {
                                caption: response.data.response,
                                sendSeen: false
                            });
                            logger.info(`Sent image with reply to ${msg.from}`);
                        } catch (imgError) {
                            logger.error('Failed to send image:', imgError.message);
                            // Fallback: send text only
                            await chat.sendMessage(response.data.response, { sendSeen: false });
                        }
                    } else {
                        logger.warn('Image file not found, sending text only');
                        await chat.sendMessage(response.data.response, { sendSeen: false });
                    }
                } else {
                    logger.debug('No category image, sending text only');
                    await chat.sendMessage(response.data.response, { sendSeen: false });
                }
                logger.info(`Sent reply to ${msg.from}`);
            } catch (sendError) {
                logger.error('chat.sendMessage failed:', sendError.message);
            }
        } else {
            logger.error('Invalid response from backend:', response.data);
            try {
                await chat.clearState();
                await chat.sendMessage("Sorry, I'm having trouble processing your request right now.", { sendSeen: false });
            } catch (e) {
                logger.error('Failed to send error message:', e.message);
            }
        }

    } catch (error) {
        logger.error('Error processing message:', error.message);
        logger.error('Stack trace:', error.stack);
        if (error.response) {
            logger.error('Backend error data:', error.response.data);
        }

        // Send user-friendly error message
        try {
            const chat = await msg.getChat();
            await chat.clearState();
            await chat.sendMessage(
                "Sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                { sendSeen: false }
            );
        } catch (sendError) {
            logger.error('Failed to send error message to user:', sendError.message);
        }
    }
}

// Listen to 'message' event (only incoming messages from others)
client.on('message', async (msg) => {
    // Extra safety: Ignore Newsletters
    if (msg.from.includes('@newsletter')) return;

    await handleMessage(msg);
});
// client.on('message_create') captures own messages too - disabling it to fix duplicates.

// Start Client
client.initialize();

// Simple health check endpoint for the node service
app.get('/health', (req, res) => {
    res.json({ status: 'ok', whatsapp_ready: client.info !== undefined });
});

app.listen(PORT, () => {
    logger.info(`WhatsApp Service listening on port ${PORT}`);
});
