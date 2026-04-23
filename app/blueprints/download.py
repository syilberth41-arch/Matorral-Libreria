"""Download blueprint — serve purchased e-books securely."""
from flask import Blueprint, send_file, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.services.download_service import DownloadService

download_bp = Blueprint('download', __name__, template_folder='templates')


@download_bp.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    """Serve digital book file only if user has purchased it."""
    if not DownloadService.can_download(current_user.id, book_id):
        flash('No tienes acceso a este libro. Debes comprarlo primero.', 'danger')
        return redirect(url_for('catalog.book_detail', book_id=book_id))

    file_path = DownloadService.get_file_path(book_id)
    
    from app.models.book import Book
    from app.extensions import db
    import unicodedata
    book = db.session.get(Book, book_id)
    
    # Create safe filename from book title
    safe_title = unicodedata.normalize('NFKD', book.title).encode('ASCII', 'ignore').decode('utf-8')
    safe_filename = f"{safe_title.replace(' ', '_')}.pdf"

    if not file_path:
        # Provide a generated dummy PDF if file is missing (for seeded data)
        import io
        # Minimal valid PDF string
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n5 0 obj\n<< /Length 61 >>\nstream\nBT\n/F1 24 Tf\n50 700 Td\n(Disfruta tu libro!) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000109 00000 n \n0000000216 00000 n \n0000000289 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n399\n%%EOF\n"
        dummy_pdf = io.BytesIO(pdf_content)
        return send_file(dummy_pdf, as_attachment=True, download_name=safe_filename, mimetype='application/pdf')

    return send_file(file_path, as_attachment=True, download_name=safe_filename)
