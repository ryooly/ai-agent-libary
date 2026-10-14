def build_prompt(text: str) -> str:
    return (
        "Expand the following brief note into a clear, well-structured, "
        "and detailed version. Keep the original intent intact.\n\n"
        f"Note:\n{text}"
    )
