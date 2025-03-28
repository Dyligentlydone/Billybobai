import express from 'express';
import twilio from 'twilio';
import { Request, Response } from 'express';
import fetch from 'node-fetch';  

const router = express.Router();

// Initialize Twilio client
const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

router.post('/preview', async (req: Request, res: Response) => {
  try {
    const { text, voice } = req.body;

    if (!text || !voice) {
      return res.status(400).json({ error: 'Missing required parameters' });
    }

    // Create TwiML for voice preview
    const twiml = new twilio.twiml.VoiceResponse();

    // For basic voices, use them directly
    if (voice === 'man' || voice === 'woman') {
      twiml.say({
        voice: voice,
      }, text);
    } else {
      // For Polly/Google voices, use the full voice name
      twiml.say({
        voice: voice, // e.g., 'Polly.Joanna' or 'Google.en-US-Standard-A'
      }, text);
    }

    // Convert TwiML to audio using Twilio Media API
    const call = await client.calls.create({
      twiml: twiml.toString(),
      to: process.env.TWILIO_PHONE_NUMBER!,
      from: process.env.TWILIO_PHONE_NUMBER!,
      record: true,
    });

    // Wait for recording to be ready
    const recording = await client.recordings(call.sid).fetch();
    const audioUrl = `https://api.twilio.com/2010-04-01/Accounts/${process.env.TWILIO_ACCOUNT_SID}/Recordings/${recording.sid}.mp3`;

    // Stream the audio back to the client
    const response = await fetch(audioUrl);
    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    res.set('Content-Type', 'audio/mpeg');
    res.send(buffer);

  } catch (error) {
    console.error('TTS Preview Error:', error);
    res.status(500).json({ error: 'Failed to generate voice preview' });
  }
});

export default router;
