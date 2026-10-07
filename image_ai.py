import os
import ollama



# =========================
# IMAGE ANALYSIS
# =========================

def analyze_image(prompt, image_bytes):

    try:

        if len(image_bytes) > 5_000_000:
            return "❌ Image too large. Please upload smaller image."

        response = ollama.chat(
            model="llava:latest",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_bytes]
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:

        return f"❌ Image AI Error: {str(e)}"