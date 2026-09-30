
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Common alternative words used in item descriptions
SYNONYMS = {
    "backpack": "bag",
    "rucksack": "bag",
    "mobile": "phone",
    "smartphone": "phone",
    "cellphone": "phone",
    "flask": "bottle",
    "metal": "steel",
    "navy": "blue",
    "grey": "gray",
    "spectacles": "glasses"
}


def normalize_text(text):
    """Clean text and replace a few common synonyms."""

    text = str(text or "").lower()

    words = re.findall(r"\b\w+\b", text)

    words = [
        SYNONYMS.get(word, word)
        for word in words
    ]

    return " ".join(words)


def calculate_matches(selected_item, candidates):
    """
    Compare one lost or found item against
    reports of the opposite type.
    """

    if not candidates:
        return []

    # Include the item name in its description.
    selected_text = normalize_text(
        selected_item["name"] + " " +
        selected_item["description"]
    )

    candidate_texts = [
        normalize_text(
            item["name"] + " " + item["description"]
        )
        for item in candidates
    ]

    # Convert all descriptions into TF-IDF vectors.
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    vectors = vectorizer.fit_transform(
        [selected_text] + candidate_texts
    )

    # Compare the selected report against each candidate.
    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )[0]

    results = []

    for item, text_score in zip(candidates, similarities):

        category_match = (
            normalize_text(selected_item["category"]) ==
            normalize_text(item["category"])
        )

        selected_color = normalize_text(
            selected_item["color"]
        )

        candidate_color = normalize_text(
            item["color"]
        )

        color_match = (
            bool(selected_color)
            and bool(candidate_color)
            and selected_color == candidate_color
        )

        selected_location = normalize_text(
            selected_item["location"]
        )

        candidate_location = normalize_text(
            item["location"]
        )

        location_match = (
            bool(selected_location)
            and bool(candidate_location)
            and (
                selected_location in candidate_location
                or candidate_location in selected_location
            )
        )

        # Weighted similarity score
        score = (
            float(text_score) * 0.70
            + int(category_match) * 0.15
            + int(color_match) * 0.10
            + int(location_match) * 0.05
        )

        results.append({
            "item": item,
            "score": round(score * 100, 2),
            "text_similarity": round(
                float(text_score) * 100, 2
            ),
            "category_match": category_match,
            "color_match": color_match,
            "location_match": location_match
        })

    # Highest-scoring results first
    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return results