from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime


def export_results_to_pdf(all_results, filename):
    print(">>> START EXPORT PDF:", filename)

    try:
        styles = getSampleStyleSheet()
        elements = []

        #  TITLE
        elements.append(Paragraph("INVENTORY RETRIEVAL SIMULATION REPORT", styles["Title"]))
        elements.append(Spacer(1, 12))

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        elements.append(Paragraph(f"Generated at: {now}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        # LOOP THROUGH ALGORITHMS
        for alg_name, result in all_results.items():
            elements.append(Paragraph(f"Algorithm: {alg_name}", styles["Heading2"]))
            elements.append(Spacer(1, 8))

            summary_text = f"""
            Total Revenue: {result.total_revenue:,.2f}<br/>
            Final Inventory: {result.inventory[-1]}<br/>
            Total Retrieved: {sum(result.retrievals):,.2f}
            """
            elements.append(Paragraph(summary_text, styles["Normal"]))
            elements.append(Spacer(1, 10))

            #  DETAILED TABLE
            table_data = [[
                "Period", "Price", "Inventory", "Retrieval",
                "δ_t", "Demand", "Sales", "Revenue",
                "Hold Cost", "Remaining"
            ]]

            for row in result.period_logs:
                table_data.append([
                    row["Period"],
                    f'{row["Price"]:.2f}',
                    f'{row["Inventory"]:.1f}',
                    f'{row["Retrieval"]:.1f}',
                    f'{row["Delta"]:.3f}',
                    f'{row["Demand"]:.1f}',
                    f'{row["Sales"]:.1f}',
                    f'{row["Revenue"]:.2f}',
                    f'{row["HoldingCost"]:.2f}',
                    f'{row["Remaining"]:.1f}',
                ])

            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 25))

        #  WRITE PDF
        doc = SimpleDocTemplate(filename, pagesize=A4)
        doc.build(elements)

        print(f"Log: PDF exported successfully to: {filename}")

    except Exception as e:
        print(">>>Log: EXPORT PDF ERROR:", e)
        raise
