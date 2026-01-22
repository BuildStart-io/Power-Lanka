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
const PORT = process.env.PORT || 3000;

// Initialize WhatsApp Client
const client = new Client({
    authStrategy: new LocalAuth(),
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
    console.log('QR RECEIVED', qr);
    qrcode.generate(qr, { small: true });
    console.log('Please scan the QR code with your WhatsApp to authenticate.');
});

// Client Ready
client.on('ready', async () => {
    console.log('WhatsApp Client is ready!');
    // Set presence to online
    try {
        await client.sendPresenceAvailable();
        console.log('Presence set to online');
    } catch (e) {
        console.error('Failed to set presence:', e.message);
    }
});

// Authentication Failure
client.on('auth_failure', msg => {
    console.error('AUTHENTICATION FAILURE', msg);
});

// Track processed messages to avoid duplicates
const processedMessages = new Set();

// Extract phone number helper
function extractPhoneNumber(waId) {
  return waId
    .replace("@c.us", "")
    .replace("@s.whatsapp.net", "")
    .replace("@lid", "");
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

        console.log(`Received message from ${msg.from}: ${msg.body}`);

        // Mark as processed
        processedMessages.add(messageId);
        // Clean up old entries (keep last 100)
        if (processedMessages.size > 100) {
            const firstKey = processedMessages.values().next().value;
            processedMessages.delete(firstKey);
        }

        // Extract phone number
        const phoneNumber = extractPhoneNumber(msg.from);

        console.log(`[DEBUG] Processing message from ${phoneNumber}`);

        // Get chat and show typing indicator
        const chat = await msg.getChat();
        await chat.sendStateTyping();
        console.log('[DEBUG] Typing indicator shown');

        const response = await axios.post(`${BACKEND_URL}/whatsapp/message`, {
            phone_number: phoneNumber,
            message: msg.body
        });

        console.log('[DEBUG] Backend response received');

        if (response.data && response.data.response) {
            // Clear typing indicator
            try {
                console.log('[DEBUG] Clearing typing state');
                await chat.clearState();

                // Check if there's a category image to send
                if (response.data.category_image) {
                    const imagePath = path.join(
                        '/home/lord/Projects/Rag_Agent',
                        response.data.category_image
                    );

                    console.log('[DEBUG] Category image path:', imagePath);

                    if (fs.existsSync(imagePath)) {
                        try {
                            console.log('[DEBUG] Sending image with caption');
                            const media = MessageMedia.fromFilePath(imagePath);
                            await chat.sendMessage(media, {
                                caption: response.data.response,
                                sendSeen: false
                            });
                            console.log(`[DEBUG] Sent image with reply to ${msg.from}`);
                        } catch (imgError) {
                            console.error('[DEBUG] Failed to send image:', imgError.message);
                            // Fallback: send text only
                            await chat.sendMessage(response.data.response, { sendSeen: false });
                        }
                    } else {
                        console.log('[DEBUG] Image file not found, sending text only');
                        await chat.sendMessage(response.data.response, { sendSeen: false });
                    }
                } else {
                    console.log('[DEBUG] No category image, sending text only');
                    await chat.sendMessage(response.data.response, { sendSeen: false });
                }
                console.log(`[DEBUG] Sent reply to ${msg.from}`);
            } catch (sendError) {
                console.error('[DEBUG] chat.sendMessage failed:', sendError.message);
            }
        } else {
            console.error('Invalid response from backend:', response.data);
            try {
                await chat.clearState();
                await chat.sendMessage("Sorry, I'm having trouble processing your request right now.", { sendSeen: false });
            } catch (e) {
                console.error('Failed to send error message:', e.message);
            }
        }

    } catch (error) {
        console.error('Error processing message:', error.message);
        console.error('Stack trace:', error.stack);
        if (error.response) {
            console.error('Backend error data:', error.response.data);
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
            console.error('Failed to send error message to user:', sendError.message);
        }
    }
}

// Listen to message_create instead of message for better reliability
client.on('message_create', async (msg) => {
    await handleMessage(msg);
});

// Start Client
client.initialize();

// Simple health check endpoint for the node service
app.get('/health', (req, res) => {
    res.json({ status: 'ok', whatsapp_ready: client.info !== undefined });
});

app.listen(PORT, () => {
    console.log(`WhatsApp Service listening on port ${PORT}`);
});
