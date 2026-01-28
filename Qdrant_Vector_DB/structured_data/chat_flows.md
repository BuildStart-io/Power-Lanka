# Chatbot & Admin Reply Rules

## 1. General Message Handling

**Scenario:** Customer sends a general message (e.g., "details", "info", "price") without specifying a product.
**Bot Reply:**
> "ඔබට අවශ්‍ය product එක මොනවද සර් / මැඩම්?
> (උදා: ChatGPT Plus / Canva / CapCut / Adobe / Meta Verify)"

## 2. Product Details Request

**Scenario:** Customer asks for details of a specific product.
**Bot Action:**

1. Send full details + price + warranty info for the requested product.
2. Ask for the customer's full name (as per NIC) to proceed.
**Bot Reply Example:**

> "ඔබට මේ service එක activate කරලා දෙන්න සම්පූර්ණ නම (NIC එකේ තියන විදිහට) send කරන්න."

## 3. Order Processing

**Scenario:** Customer sends their name.
**Bot Action:** Start order confirmation and payment steps.

## Bot Training Summary

* **❓ Unclear message** → Ask which product.
* **📦 Product details sent** → Ask for full name.
* **🧾 Name received** → Proceed with order.
