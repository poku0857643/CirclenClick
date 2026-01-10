"""
Enhanced Claims Database
Contains common misinformation and verified facts for local verification
"""

from typing import Dict, List, Tuple
from core.models import Verdict

class ClaimsDatabase:
    """Database of known claims with verdicts and evidence"""

    # Known FALSE claims (common misinformation)
    FALSE_CLAIMS = {
        "earth is flat": {
            "verdict": Verdict.FALSE,
            "confidence": 99.0,
            "explanation": "The Earth is an oblate spheroid. This has been proven through satellite imagery, physics, and centuries of scientific observation.",
            "evidence": [
                "Satellite images show Earth's curvature",
                "Ships disappear hull-first over the horizon",
                "Different star constellations visible from different latitudes",
                "Lunar eclipses show Earth's round shadow on the moon"
            ],
            "sources": ["NASA", "National Geographic", "Scientific consensus"]
        },

        "vaccines cause autism": {
            "verdict": Verdict.FALSE,
            "confidence": 98.0,
            "explanation": "Multiple large-scale studies involving millions of children have found no link between vaccines and autism. The original study claiming this was retracted due to fraud.",
            "evidence": [
                "Wakefield's 1998 study was retracted and author lost medical license",
                "Meta-analysis of 1.2 million children found no correlation",
                "CDC, WHO, and major medical organizations confirm vaccine safety",
                "Autism diagnoses continue rising in unvaccinated populations"
            ],
            "sources": ["CDC", "WHO", "The Lancet (retraction)", "PubMed"]
        },

        "5g causes covid": {
            "verdict": Verdict.FALSE,
            "confidence": 99.0,
            "explanation": "COVID-19 is caused by the SARS-CoV-2 virus, not by radio waves. The virus spread to countries without 5G networks, and viruses cannot be transmitted via radio frequencies.",
            "evidence": [
                "COVID-19 spread to countries without 5G infrastructure",
                "Viruses require biological hosts and cannot travel on radio waves",
                "COVID-19 is caused by SARS-CoV-2 virus (proven via sequencing)",
                "Radio waves are non-ionizing and cannot damage DNA"
            ],
            "sources": ["WHO", "CDC", "IEEE", "Full Fact"]
        },

        "climate change is a hoax": {
            "verdict": Verdict.FALSE,
            "confidence": 97.0,
            "explanation": "97% of climate scientists agree that climate change is real and primarily caused by human activities. Evidence includes rising global temperatures, melting ice caps, and increasing CO2 levels.",
            "evidence": [
                "Global temperature increased 1.1°C since pre-industrial times",
                "CO2 levels at highest in 800,000 years",
                "97% scientific consensus on human-caused climate change",
                "Observable effects: melting glaciers, rising sea levels, extreme weather"
            ],
            "sources": ["IPCC", "NASA", "NOAA", "Nature Climate Change"]
        },

        "moon landing was faked": {
            "verdict": Verdict.FALSE,
            "confidence": 99.0,
            "explanation": "The Apollo moon landings were real and verified by multiple independent sources including other countries. Evidence includes moon rocks, reflectors still on the lunar surface, and independent tracking.",
            "evidence": [
                "382 kg of moon rocks brought back and analyzed worldwide",
                "Lunar laser reflectors still used by scientists today",
                "Soviet Union confirmed landings (Cold War enemy)",
                "High-resolution photos from lunar orbit show landing sites"
            ],
            "sources": ["NASA", "Smithsonian", "Independent observatories"]
        },

        "microchips in vaccines": {
            "verdict": Verdict.FALSE,
            "confidence": 99.0,
            "explanation": "Vaccines do not contain microchips. Modern microchips require power sources and are far too large to fit through a vaccine needle.",
            "evidence": [
                "Vaccine ingredients are publicly listed and tested",
                "Microchips require power sources and are visible to naked eye",
                "Vaccine needles are too small for current chip technology",
                "No evidence in scientific analysis of any vaccine"
            ],
            "sources": ["Reuters Fact Check", "Snopes", "FDA"]
        },

        "drinking bleach cures": {
            "verdict": Verdict.FALSE,
            "confidence": 100.0,
            "explanation": "Drinking bleach or disinfectants is extremely dangerous and potentially fatal. It does not cure any disease and causes severe internal damage.",
            "evidence": [
                "FDA explicitly warns against ingesting disinfectants",
                "Bleach causes chemical burns to digestive system",
                "Poison control centers report serious injuries from ingestion",
                "No medical evidence of any health benefits"
            ],
            "sources": ["FDA", "CDC", "Poison Control", "WHO"]
        },

        "covid vaccine changes dna": {
            "verdict": Verdict.FALSE,
            "confidence": 98.0,
            "explanation": "mRNA vaccines do not alter DNA. mRNA cannot integrate into DNA and breaks down quickly after producing the spike protein to trigger immune response.",
            "evidence": [
                "mRNA never enters the cell nucleus where DNA is stored",
                "mRNA degrades within days after vaccination",
                "Reverse transcription (RNA to DNA) requires specific enzymes not present",
                "Confirmed through multiple peer-reviewed studies"
            ],
            "sources": ["CDC", "Nature Medicine", "Johns Hopkins", "MIT"]
        },
    }

    # Known TRUE statements (verified facts)
    TRUE_CLAIMS = {
        "water boils at 100 degrees celsius": {
            "verdict": Verdict.TRUE,
            "confidence": 100.0,
            "explanation": "At sea level atmospheric pressure (1 atm), pure water boils at 100°C (212°F).",
            "evidence": ["Fundamental physics constant", "Verified in countless experiments"],
            "sources": ["Physics textbooks", "NIST"]
        },

        "earth orbits the sun": {
            "verdict": Verdict.TRUE,
            "confidence": 100.0,
            "explanation": "Earth orbits the Sun in an elliptical path, completing one orbit approximately every 365.25 days.",
            "evidence": [
                "Confirmed by centuries of astronomical observations",
                "Explains seasonal changes",
                "Verified by space missions and satellites"
            ],
            "sources": ["NASA", "Astronomical consensus"]
        },

        "smoking causes cancer": {
            "verdict": Verdict.TRUE,
            "confidence": 99.0,
            "explanation": "Smoking tobacco significantly increases the risk of lung cancer and other cancers. This has been proven through decades of research.",
            "evidence": [
                "Tobacco smoke contains 70+ known carcinogens",
                "Lung cancer rates 15-30x higher in smokers",
                "Risk decreases after quitting",
                "Confirmed in millions of cases worldwide"
            ],
            "sources": ["WHO", "American Cancer Society", "CDC", "NIH"]
        },

        "antibiotics don't work on viruses": {
            "verdict": Verdict.TRUE,
            "confidence": 99.0,
            "explanation": "Antibiotics only work against bacterial infections, not viral infections. Using antibiotics for viruses is ineffective and contributes to antibiotic resistance.",
            "evidence": [
                "Antibiotics target bacterial cell walls/processes",
                "Viruses lack these structures",
                "Misuse leads to antibiotic-resistant bacteria",
                "Standard medical practice worldwide"
            ],
            "sources": ["CDC", "WHO", "Medical consensus"]
        },
    }

    # MISLEADING claims (contains truth but lacks context)
    MISLEADING_CLAIMS = {
        "vaccines contain mercury": {
            "verdict": Verdict.MISLEADING,
            "confidence": 75.0,
            "explanation": "Some vaccines previously contained thimerosal (ethylmercury) as a preservative, which is different from harmful methylmercury. It has been removed from most childhood vaccines since 2001 as a precaution, despite no evidence of harm.",
            "evidence": [
                "Thimerosal (ethylmercury) is different from methylmercury",
                "Removed from most childhood vaccines since 2001",
                "Studies found no link to autism or neurological problems",
                "Still used safely in some flu vaccines in trace amounts"
            ],
            "sources": ["FDA", "CDC", "WHO"]
        },

        "sugar makes kids hyperactive": {
            "verdict": Verdict.MISLEADING,
            "confidence": 70.0,
            "explanation": "Multiple controlled studies have found no direct link between sugar consumption and hyperactivity. However, sugary foods are often consumed at exciting events, creating an association.",
            "evidence": [
                "Double-blind studies show no sugar-hyperactivity link",
                "Parental expectation affects perception",
                "Context (parties, holidays) may cause observed behavior",
                "Excessive sugar has other health concerns (obesity, dental)"
            ],
            "sources": ["Journal of the American Medical Association", "Yale Medicine"]
        },
    }

    @classmethod
    def search(cls, claim: str) -> Tuple[bool, Dict]:
        """
        Search for a claim in the database

        Returns:
            (found, claim_data) tuple
        """
        claim_lower = claim.lower().strip()

        # Check FALSE claims
        for key, data in cls.FALSE_CLAIMS.items():
            if key in claim_lower or cls._fuzzy_match(key, claim_lower):
                return True, data

        # Check TRUE claims
        for key, data in cls.TRUE_CLAIMS.items():
            if key in claim_lower or cls._fuzzy_match(key, claim_lower):
                return True, data

        # Check MISLEADING claims
        for key, data in cls.MISLEADING_CLAIMS.items():
            if key in claim_lower or cls._fuzzy_match(key, claim_lower):
                return True, data

        return False, {}

    @classmethod
    def _fuzzy_match(cls, key: str, claim: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy matching for variations"""
        key_words = set(key.split())
        claim_words = set(claim.split())

        if not key_words:
            return False

        # Calculate word overlap
        overlap = len(key_words & claim_words) / len(key_words)
        return overlap >= threshold

    @classmethod
    def get_stats(cls) -> Dict:
        """Get database statistics"""
        return {
            "total_claims": len(cls.FALSE_CLAIMS) + len(cls.TRUE_CLAIMS) + len(cls.MISLEADING_CLAIMS),
            "false_claims": len(cls.FALSE_CLAIMS),
            "true_claims": len(cls.TRUE_CLAIMS),
            "misleading_claims": len(cls.MISLEADING_CLAIMS),
        }
