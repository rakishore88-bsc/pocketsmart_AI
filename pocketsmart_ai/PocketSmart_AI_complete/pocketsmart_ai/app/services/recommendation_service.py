from __future__ import annotations

from app.models.schemas import (
    BudgetAllocation,
    HomeRequest,
    JewelryRequest,
    PartyRequest,
    RecommendationItem,
    RecommendationResponse,
)


def platform_url(platform: str, query: str) -> str:
    from urllib.parse import quote_plus
    q = quote_plus(query)
    return {
        "Amazon": f"https://www.amazon.in/s?k={q}",
        "Flipkart": f"https://www.flipkart.com/search?q={q}",
        "IKEA": f"https://www.ikea.com/in/en/search/?q={q}",
        "Swiggy": f"https://www.swiggy.com/search?query={q}",
        "Zomato": f"https://www.zomato.com/search?q={q}",
        "OYO": f"https://www.oyorooms.com/search?location={q}",
    }.get(platform, "#")


def home_fallback(data: HomeRequest) -> RecommendationResponse:
    allocations = [
        BudgetAllocation(category="Furniture", amount=data.budget * .35, percentage=35, rationale="Prioritize high-use furniture pieces."),
        BudgetAllocation(category="Lighting", amount=data.budget * .15, percentage=15, rationale="Layer ambient and task lighting."),
        BudgetAllocation(category="Decor", amount=data.budget * .20, percentage=20, rationale="Use decor to establish the chosen style."),
        BudgetAllocation(category="Storage", amount=data.budget * .20, percentage=20, rationale="Reserve budget for practical storage."),
        BudgetAllocation(category="Contingency", amount=data.budget * .10, percentage=10, rationale="Keep a buffer for delivery and price changes."),
    ]
    items = [
        RecommendationItem(name="Minimalist 3-Seater Sofa", category="Furniture", estimated_price=data.budget*.18, currency=data.currency, platform="Amazon", url=platform_url("Amazon", "minimalist 3 seater sofa"), reason=f"Works well for {', '.join(data.rooms)} with a {data.style} direction.", priority="high"),
        RecommendationItem(name="Warm LED Ceiling Light", category="Lighting", estimated_price=data.budget*.06, currency=data.currency, platform="IKEA", url=platform_url("IKEA", "LED ceiling light"), reason="Adds practical ambient lighting without consuming a large share of the budget.", priority="high"),
        RecommendationItem(name="Decorative Wall Art Set", category="Decor", estimated_price=data.budget*.07, currency=data.currency, platform="Flipkart", url=platform_url("Flipkart", "decorative wall art set"), reason="Adds visual character while keeping the spend controlled.", priority="medium"),
        RecommendationItem(name="Modular Storage Unit", category="Storage", estimated_price=data.budget*.12, currency=data.currency, platform="IKEA", url=platform_url("IKEA", "modular storage unit"), reason="Supports organization and long-term utility.", priority="medium"),
    ]
    return RecommendationResponse(planner="home", title="Home Interior Budget Plan", summary=f"A balanced {data.style} plan for {', '.join(data.rooms)} within your {data.currency} {data.budget:,.0f} budget.", budget=data.budget, currency=data.currency, budget_allocations=allocations, recommendations=items, tips=["Measure spaces before ordering large furniture.", "Compare delivery and installation charges before checkout.", "Buy foundational furniture first, then use decor to finish the look."])


def party_fallback(data: PartyRequest) -> RecommendationResponse:
    allocations = [
        BudgetAllocation(category="Food", amount=data.budget*.45, percentage=45, rationale="Food is usually the largest variable cost for guest-driven events."),
        BudgetAllocation(category="Venue", amount=data.budget*.25, percentage=25, rationale="Keep venue cost proportional to the guest count."),
        BudgetAllocation(category="Decoration", amount=data.budget*.15, percentage=15, rationale="Use focused decorations for visual impact."),
        BudgetAllocation(category="Entertainment", amount=data.budget*.10, percentage=10, rationale="Reserve a controlled amount for activities or music."),
        BudgetAllocation(category="Contingency", amount=data.budget*.05, percentage=5, rationale="Cover small last-minute expenses."),
    ]
    per_guest = data.budget / data.guests
    items = [
        RecommendationItem(name="Catering Package Search", category="Food", estimated_price=data.budget*.45, currency=data.currency, platform="Swiggy", url=platform_url("Swiggy", f"{data.event_type} catering"), reason=f"Targets an average overall spend of about {data.currency} {per_guest:,.0f} per guest.", priority="high"),
        RecommendationItem(name="Local Event Catering Options", category="Food", estimated_price=data.budget*.45, currency=data.currency, platform="Zomato", url=platform_url("Zomato", f"{data.event_type} catering"), reason="Useful for comparing nearby food providers and menus.", priority="medium"),
        RecommendationItem(name="Budget Venue Search", category="Venue", estimated_price=data.budget*.25, currency=data.currency, platform="OYO", url=platform_url("OYO", data.venue_area or "event venue"), reason="Provides a starting point for accommodation or event-space research.", priority="medium"),
        RecommendationItem(name="Party Decoration Set", category="Decoration", estimated_price=data.budget*.15, currency=data.currency, platform="Amazon", url=platform_url("Amazon", f"{data.event_type} party decorations"), reason="Keeps decoration spend aligned with the allocation.", priority="medium"),
    ]
    return RecommendationResponse(planner="party", title=f"{data.event_type.title()} Party Budget Plan", summary=f"A {data.currency} {data.budget:,.0f} plan for {data.guests} guests, with food, venue, decoration and entertainment allocations.", budget=data.budget, currency=data.currency, budget_allocations=allocations, recommendations=items, tips=["Confirm guest count before ordering catering.", "Ask vendors what taxes, delivery, setup and service charges are included.", "Keep a small contingency for last-minute changes."])


def jewelry_fallback(data: JewelryRequest) -> RecommendationResponse:
    allocations = [
        BudgetAllocation(category="Main Jewelry", amount=data.budget*.65, percentage=65, rationale="Spend most of the budget on the focal piece."),
        BudgetAllocation(category="Secondary Piece", amount=data.budget*.20, percentage=20, rationale="Add a complementary item without overloading the look."),
        BudgetAllocation(category="Accessories", amount=data.budget*.10, percentage=10, rationale="Reserve a little for finishing details."),
        BudgetAllocation(category="Contingency", amount=data.budget*.05, percentage=5, rationale="Allow for price variation."),
    ]
    query = f"{data.occasion} {data.style} {data.metal} jewelry"
    items = [
        RecommendationItem(name="Statement Earrings", category="Main Jewelry", estimated_price=data.budget*.35, currency=data.currency, platform="Amazon", url=platform_url("Amazon", query + " statement earrings"), reason="A versatile focal piece for the selected occasion and style.", priority="high"),
        RecommendationItem(name="Matching Necklace", category="Secondary Piece", estimated_price=data.budget*.30, currency=data.currency, platform="Flipkart", url=platform_url("Flipkart", query + " necklace"), reason="Creates a coordinated look while staying within the allocation.", priority="medium"),
        RecommendationItem(name="Minimal Bracelet", category="Accessories", estimated_price=data.budget*.10, currency=data.currency, platform="Amazon", url=platform_url("Amazon", query + " bracelet"), reason="Adds a subtle finishing layer.", priority="low"),
    ]
    return RecommendationResponse(planner="jewelry", title="Jewelry Budget Plan", summary=f"Jewelry suggestions for a {data.occasion} occasion with a {data.style} style direction and {data.currency} {data.budget:,.0f} budget.", budget=data.budget, currency=data.currency, budget_allocations=allocations, recommendations=items, tips=["Check exact measurements and material details before purchase.", "If using an outfit image, treat the AI's color/style analysis as guidance rather than a guarantee.", "Compare return policies before ordering fashion accessories online."])
