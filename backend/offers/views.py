from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from drives.models import PlacementDrive

from .services import decode_offer, detect_red_flags


def _num(data, key):
    v = data.get(key)
    if v in (None, ""):
        return None
    try:
        d = Decimal(str(v))
    except InvalidOperation:
        raise ValueError(f"{key} must be a number.")
    if d < 0:
        raise ValueError(f"{key} cannot be negative.")
    return d


class DecodeView(APIView):
    """POST manual numbers to decode a CTC."""
    def post(self, request):
        try:
            args = {k: _num(request.data, k) for k in ("ctc_total", "fixed", "variable", "joining_bonus", "other")}
            pct = _num(request.data, "assumed_variable_percent")
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        if pct is not None and pct > 100:
            return Response({"detail": "assumed_variable_percent must be 0-100."}, status=400)
        return Response(decode_offer(args["ctc_total"], args["fixed"], args["variable"], args["joining_bonus"],
                                     args["other"], pct))


class DriveOfferView(APIView):
    """Decode + red flags using the terms stored for a drive."""
    def get(self, request, drive_id):
        d = get_object_or_404(PlacementDrive, pk=drive_id)
        return Response({"decoder": decode_offer(d.ctc_total, d.ctc_fixed, d.ctc_variable, d.joining_bonus,
                                                 d.other_components),
                         "red_flags": detect_red_flags(d), "terms_notes": d.terms_notes})
