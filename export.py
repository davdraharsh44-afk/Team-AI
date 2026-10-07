from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# =========================
# EXPORT CHAT TO PDF
# =========================

def export_chat_to_pdf(messages, filename="chat.pdf"):
    try:
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4
        )

        story = []

        for message in messages:
            sender = message.get("sender", "")
            text = message.get("message", "")

            story.append(
                Paragraph(
                    f"<b>{sender}:</b> {text}",
                    styles["Normal"]
                )
            )

        doc.build(story)

        return filename

    except Exception as e:
        print("PDF Export Error:", e)
        return None