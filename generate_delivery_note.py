from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

INPUT_FILE = "test_report_output.txt"
OUTPUT_FILE = "delivery_note.pdf"

def generate_pdf():
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Bon de Livraison - Résultat des Tests")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Date : {datetime.now().isoformat(sep=' ', timespec='seconds')}")

    c.setFont("Helvetica", 11)
    y = height - 120

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = ["Aucun rapport de test trouvé."]

    for line in lines:
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50

        c.drawString(50, y, line.strip())
        y -= 18

    c.save()
    print(f"PDF generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_pdf()