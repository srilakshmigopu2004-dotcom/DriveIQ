from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from drives.models import PlacementDrive
from users.views import get_profile

from .services.difficulty import analyze_difficulty
from .services.eligibility import check_eligibility
from .services.readiness import analyze_readiness
from .services.recommendations import recommend
from .services.scoring import compute_match
from .services.utils import format_inr


def _drive(pk):
    return get_object_or_404(PlacementDrive.objects.select_related("company", "job_role")
                             .prefetch_related("required_skills", "rounds"), pk=pk)


class EligibilityView(APIView):
    def get(self, request, drive_id):
        return Response(check_eligibility(get_profile(request.user), _drive(drive_id)))


class MatchView(APIView):
    def get(self, request, drive_id):
        return Response(compute_match(get_profile(request.user), _drive(drive_id)))


class RecommendationView(APIView):
    def get(self, request):
        return Response(recommend(get_profile(request.user), 10))


class CompareView(APIView):
    """Side-by-side facts only. No 'best company' is declared on purpose."""
    def get(self, request):
        try:
            ids = [int(x) for x in request.query_params.get("drives", "").split(",") if x][:4]
        except ValueError:
            return Response({"detail": "drives must be comma-separated ids."}, status=400)
        if len(ids) < 2:
            return Response({"detail": "Pick at least 2 drives (max 4)."}, status=400)
        profile = get_profile(request.user)
        rows = []
        for pk in ids:
            d = _drive(pk)
            elig = check_eligibility(profile, d)
            m = compute_match(profile, d, elig, analyze_readiness(profile, d))
            rows.append({"drive_id": d.id, "company": d.company.name, "role": d.title,
                         "ctc": format_inr(d.ctc_total) or "Not specified", "location": d.location or "Not specified",
                         "min_cgpa": str(d.min_cgpa) if d.min_cgpa is not None else "No minimum",
                         "eligible": elig["verdict"], "match_score": m["match_score"],
                         "difficulty": analyze_difficulty(d)["label"], "rounds": d.rounds.count(),
                         "bond": f"{d.bond_years} years" if d.bond_years else
                                 ("Not specified" if d.bond_years is None else "None")})
        return Response({"drives": rows, "note": "Compare the factors that matter to you; DriveIQ does not rank companies."})
