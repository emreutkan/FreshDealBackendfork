# services/report_service.py
from src.models import db, PurchaseReport, Purchase, Restaurant, Listing

def create_purchase_report_service(user_id, purchase_id, image_url, description):
    """
    Create a report about a specific purchase.
    Includes an optional user-uploaded image and a brief explanation.
    Enforces:
      - The purchase must exist and belong to the user.
      - The user can report a purchase only once.
    """
    try:
        # Verify the purchase exists and belongs to this user.
        purchase = Purchase.query.filter_by(id=purchase_id, user_id=user_id).first()
        if not purchase:
            return {"message": "Purchase not found or does not belong to the user."}, 404

        # Check if this purchase has already been reported by the same user.
        existing_report = PurchaseReport.query.filter_by(user_id=user_id, purchase_id=purchase_id).first()
        if existing_report:
            return {"message": "You have already reported this purchase."}, 400

        # Optionally fetch the listing & restaurant
        listing = purchase.listing

        # Create a new report
        report = PurchaseReport(
            user_id=user_id,
            purchase_id=purchase_id,
            restaurant_id=listing.restaurant_id if listing else None,
            listing_id=listing.id if listing else None,
            image_url=image_url,
            description=description
        )

        db.session.add(report)
        db.session.commit()

        return {
            "message": "Report created successfully",
            "report_id": report.id
        }, 201

    except Exception as e:
        db.session.rollback()
        return {
            "message": "An error occurred while creating the report",
            "error": str(e)
        }, 500


def get_user_reports_service(user_id):
    """
    Return all reports made by a specific user.
    """
    try:
        reports = PurchaseReport.query.filter_by(user_id=user_id).all()
        if not reports:
            return {"message": "No reports found for this user"}, 200

        data = []
        for r in reports:
            data.append({
                "report_id": r.id,
                "purchase_id": r.purchase_id,
                "listing_id": r.listing_id,
                "restaurant_id": r.restaurant_id,
                "image_url": r.image_url,
                "description": r.description,
                "reported_at": r.reported_at.isoformat() if r.reported_at else None
            })

        return {"reports": data}, 200

    except Exception as e:
        return {
            "message": "An error occurred while fetching user reports",
            "error": str(e)
        }, 500
