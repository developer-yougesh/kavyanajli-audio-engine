# ⏰ Kavyanjali Audio Engine - Space Keep-Alive Worker

[![Nightly HF Spaces Wakeup Call](https://github.com/developer-yougesh/kavyanjali-audio-engine/actions/workflows/wakeup_spaces.yml/badge.svg)](https://github.com/developer-yougesh/kavyanjali-audio-engine/actions/workflows/wakeup_spaces.yml)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Platform](https://img.shields.io/badge/Platform-GitHub%20Actions-blue)

This repository serves as an automated **Keep-Alive & Wakeup Service** for the **Kavyanjali AI Audio Infrastructure** deployed on Hugging Face Spaces.

---

## 🎯 Purpose

Hugging Face Spaces (CPU & ZeroGPU instances) automatically enter **Sleep Mode** after a period of inactivity. This worker prevents cold starts and response delays by sending scheduled automated wake-up pings to all TTS audio engines.

It ensures that when users request poem narrations in the **Kavyanjali Android App**, the audio processing pipeline starts **instantly without lag**.

---

## ⚡ How It Works

1. **Automated Cron Scheduling:** Powered by **GitHub Actions**, a scheduled cron job runs daily at **12:00 AM IST (18:30 UTC)**.
2. **Silent Ping Execution:** The workflow issues lightweight background `HTTP GET` requests to all active backend endpoints.
3. **Timer Reset:** This ping resets the Hugging Face sleep timer, keeping the TTS models warmed up and **perpetually active (24/7)**.

---

## 🎙️ Monitored Services

| Service Name | Language / Engine | Dedicated Space Endpoint |
| :--- | :--- | :--- |
| **Hindi Backend** | Hindi (Kokoro TTS / Edge) | `developer-yougesh-kavyanjali-hindi-backend.hf.space` |
| **English Backend** | English (Kokoro TTS / Edge) | `developer-yougesh-kavyanjali-english-backend.hf.space` |
| **Edge English Worker** | English-Male/Female + BGM Overlay | `developer-yougesh-kavyanjali-edge-backend.hf.space` |
| **Edge Hindi Worker** | Hindi-Male/Female + BGM Overlay | `developer-yougesh-kavyanjali-edge-backend.hf.space` |

---

## 🛠️ Manual Trigger

Apart from the automated nightly schedule, the wake-up ping can also be triggered manually:
1. Navigate to the **[Actions](../../actions)** tab.
2. Select **Nightly HF Spaces Wakeup Call**.
3. Click **Run workflow** ➔ **Main**.

---

<p align="center">
  <b>ONS — OM NAMAH SHIVAY</b><br>
  <i>Building trustworthy, high-performance & transparent solutions for Kavyanjali.</i>
</p>
