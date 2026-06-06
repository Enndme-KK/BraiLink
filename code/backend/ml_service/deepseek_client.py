# -*- coding: utf-8 -*-
"""
DeepSeek AI chat client via SiliconFlow (OpenAI-compatible) API.
All comments, docstrings, logs, and error messages are English-only to avoid
non-ASCII source issues in some environments.
"""
import httpx
from decouple import config
import json

# SiliconFlow / DeepSeek API configuration
DEEPSEEK_API_KEY = config('DEEPSEEK_API_KEY', default='')
_raw_url = config('DEEPSEEK_API_URL', default='https://api.deepseek.com/v1/chat/completions')
# Ensure URL ends with /chat/completions (robust against misconfigured .env)
if not _raw_url.rstrip('/').endswith('/chat/completions'):
    _raw_url = _raw_url.rstrip('/') + '/chat/completions'
DEEPSEEK_API_URL = _raw_url
DEEPSEEK_MODEL = config('DEEPSEEK_MODEL', default='deepseek-chat')


def build_system_prompt(patient_info=None, scan_result=None):
    """Build system prompt.

    Note:
    - The assistant should answer in Simplified Chinese (zh-Hans), but the
      prompt text here is English-only to keep the source ASCII.
    - You can tune the instructions as needed.
    """
    patient_info = patient_info or {}
    system_prompt = (
        "You are a professional and empathetic AI assistant. "
        "You can handle both general-purpose Q&A and medical Q&A (especially about brain tumors).\n"
        "Please decide the user intent first:\n"
        "- If it is a general topic (e.g., learning, tech, travel, life tips, common knowledge, small talk),\n"
        "  answer in a friendly, accurate, and concise manner.\n"
        "- If it is a medical topic (especially brain tumors and imaging), switch to a 'Medical Advisor Mode'\n"
        "  and follow stricter medical safety guidelines.\n\n"
        "[Patient Profile (if provided)]\n"
        f"- Name: {patient_info.get('name', 'N/A')}\n"
        f"- Age: {patient_info.get('age', 'N/A')}\n"
        f"- Gender: {patient_info.get('gender', 'N/A')}\n"
        f"- Medical history: {patient_info.get('medical_history', 'None')}\n\n"
        "[Latest Scan Result (if provided)]\n"
    )

    if scan_result:
        system_prompt += (
            f"- Scan mode: {scan_result.get('scan_mode', 'unknown')}\n"
            f"- Tumor detected: {'Yes' if scan_result.get('tumor_detected') else 'No'}\n"
            f"- Confidence: {scan_result.get('confidence_score', 0) * 100:.1f}%\n"
            f"- Tumor area (pixels): {scan_result.get('tumor_area', 0)}\n"
            f"- Analysis: {scan_result.get('analysis', 'N/A')}\n\n"
        )

    system_prompt += (
        "[Medical Advisor Mode Responsibilities]\n"
        "1. Provide reliable evidence-based medical information.\n"
        "2. Explain MRI results (T1, T2, T1CE, FLAIR).\n"
        "3. Answer questions about brain tumor diagnosis, treatment, and rehabilitation.\n"
        "4. Offer psychological support and health advice.\n\n"
        "[Medical Advisor Mode Safety Rules]\n"
        "1. Emergency: for severe headache, loss of consciousness, or limb weakness, advise immediate medical care.\n"
        "2. Diagnostic limitation: do not make final diagnoses; recommend in-person consultation.\n"
        "3. Medication safety: do not provide specific drug names/dosages; advise consulting the attending physician.\n"
        "4. Scientific rigor: be accurate and avoid misleading claims.\n"
        "5. Human care: be empathetic and patient.\n\n"
        "[General Q&A Principles]\n"
        "- Be polite, friendly, and accurate.\n"
        "- Provide examples, steps, checklists, or references if appropriate.\n"
        "- Refuse illegal, dangerous, or inappropriate requests.\n\n"
        "[Output Style]\n"
        "- Keep answers concise with bullet points when helpful.\n"
        "- IMPORTANT: Answer in Simplified Chinese (zh-Hans).\n"
    )
    return system_prompt


def chat_with_deepseek(messages, patient_info=None, scan_result=None):
    """Non-streaming chat call to DeepSeek. Returns the whole response."""
    if not DEEPSEEK_API_KEY:
        return {
            'success': False,
            'response': 'AI chat service is unavailable. Please configure DEEPSEEK_API_KEY or contact support.',
            'error': 'API_KEY_NOT_CONFIGURED'
        }

    system_prompt = build_system_prompt(patient_info, scan_result)
    chat_messages = [{"role": "system", "content": system_prompt}]
    chat_messages.extend(messages or [])

    # Log request
    print("\n" + "=" * 50)
    print("AI chat request")
    print(f"Patient: {patient_info.get('name', 'N/A')}")
    print(f"Message count: {len(messages or [])}")
    if scan_result:
        print(f"With scan result: {scan_result.get('scan_mode', 'unknown')}")
    print("=" * 50 + "\n")

    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': DEEPSEEK_MODEL,
            'messages': chat_messages,
            'max_tokens': 2000,
            'temperature': 0.7,
            'top_p': 0.9,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'stream': False
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

        print("AI reply success")
        print(f"Token usage: {usage.get('total_tokens', 0)}")
        print()

        return {
            'success': True,
            'response': ai_response,
            'usage': usage,
            'model': DEEPSEEK_MODEL
        }

    except httpx.HTTPStatusError as e:
        status = None
        body = ''
        try:
            status = e.response.status_code
            body = e.response.text
        except Exception:
            pass
        error_msg = f"API request failed (status: {status})"
        print(f"ERROR {error_msg} body={body}")
        return {
            'success': False,
            'response': f'AI service is temporarily unavailable. {error_msg}',
            'error': 'API_ERROR',
            'status': status,
            'detail': body
        }
    except httpx.TimeoutException:
        print("ERROR AI request timeout")
        return {
            'success': False,
            'response': 'AI request timed out. Please try again later or contact a doctor.',
            'error': 'TIMEOUT'
        }
    except Exception as e:
        print(f"ERROR unexpected: {str(e)}")
        return {
            'success': False,
            'response': 'AI service encountered an unexpected error. Please try again later.',
            'error': 'INTERNAL_ERROR'
        }


def chat_with_deepseek_stream(messages, patient_info=None, scan_result=None):
    """Streaming chat call. Returns a generator yielding partial content strings."""
    if not DEEPSEEK_API_KEY:
        def gen_err():
            yield 'AI chat service is unavailable. Please configure DEEPSEEK_API_KEY or contact support.'
        return gen_err()

    system_prompt = build_system_prompt(patient_info, scan_result)
    chat_messages = [{"role": "system", "content": system_prompt}]
    chat_messages.extend(messages or [])

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': DEEPSEEK_MODEL,
        'messages': chat_messages,
        'max_tokens': 2000,
        'temperature': 0.7,
        'top_p': 0.9,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        'stream': True
    }

    def _stream_gen():
        try:
            with httpx.Client(timeout=None) as client:
                with client.stream("POST", DEEPSEEK_API_URL, headers=headers, json=payload) as resp:
                    resp.raise_for_status()
                    for raw_line in resp.iter_lines():
                        if not raw_line:
                            continue
                        try:
                            line = raw_line.decode('utf-8') if isinstance(raw_line, (bytes, bytearray)) else str(raw_line)
                        except Exception:
                            continue
                        if not line.startswith('data:'):
                            continue
                        data = line[5:].strip()
                        if not data:
                            continue
                        if data == '[DONE]':
                            break
                        try:
                            obj = json.loads(data)
                            content = ''
                            choices = obj.get('choices') or []
                            if choices:
                                first = choices[0]
                                delta = first.get('delta') or {}
                                content = delta.get('content') or ''
                                if not content:
                                    message = first.get('message') or {}
                                    content = message.get('content') or ''
                            if content:
                                yield content
                        except Exception:
                            # Ignore non-JSON or parse errors
                            continue
        except httpx.HTTPStatusError as e:
            status = None
            body = ''
            try:
                status = e.response.status_code
                body = e.response.text
            except Exception:
                pass
            yield f"[stream error] API request failed: {status} {body}"
        except httpx.TimeoutException:
            yield "[stream error] AI request timeout"
        except Exception as e:
            yield f"[stream error] unexpected error: {str(e)}"

    return _stream_gen()
