from typing import List


class DesignSuggestion:
    def __init__(
        self, symbols: List[str], color_palette: List[str], notes: str
    ) -> None:
        self.symbols = symbols
        self.color_palette = color_palette
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "symbols": self.symbols,
            "colorPalette": self.color_palette,
            "notes": self.notes,
        }


class SimpleRAGEngine:
    """Very simple, rule-based placeholder for a RAG engine.

    Replace this with a real pipeline (embeddings + vector store + LLM)
    when you are ready.
    """

    def suggest(self, brief: str) -> DesignSuggestion:
        brief_lower = brief.lower()

        symbols: List[str] = []
        colors: List[str] = []
        notes_parts: List[str] = []

        if "nature" in brief_lower or "eco" in brief_lower:
            symbols.extend(["leaf", "tree", "water droplet"])
            colors.extend(["#2e7d32", "#66bb6a", "#a5d6a7"])
            notes_parts.append(
                "Leverage organic shapes and soft gradients to convey sustainability."
            )

        if "finance" in brief_lower or "bank" in brief_lower or "crypto" in brief_lower:
            symbols.extend(["shield", "line chart", "coin"])
            colors.extend(["#1a237e", "#283593", "#3949ab"])
            notes_parts.append(
                "Use strong geometric forms to signal trust and stability."
            )

        if "tech" in brief_lower or "saas" in brief_lower or "software" in brief_lower:
            symbols.extend(["circuit", "cloud", "spark"])
            colors.extend(["#0d47a1", "#1976d2", "#42a5f5"])
            notes_parts.append("Consider minimal, flat iconography with subtle motion.")

        if not symbols:
            symbols = ["abstract mark", "monogram"]
            colors = ["#424242", "#9e9e9e", "#e0e0e0"]
            notes_parts.append(
                "Start from simple shapes and a limited palette, then iterate based on user testing."
            )

        notes = " ".join(notes_parts)
        return DesignSuggestion(symbols=symbols, color_palette=colors, notes=notes)
