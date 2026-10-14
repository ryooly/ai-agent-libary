from typing import Callable, Optional

from .build_prompt import build_prompt


def expand_note(
    text: str,
    llm: Optional[Callable[[str], str]] = None,
) -> str:
    prompt = build_prompt(text)

    if llm is None:
        raise NotImplementedError("LLM function is not wired up yet. Pass an llm callable.")

    return llm(prompt)



# Cara kerjanya nantit kita menambahkan tools 2 (melabarkan teks, dan mengubah bentuknya menjadi input api notion), jadi pertama dia akan memanggil expand dulu setelah didapatkan dan diverifikasi berhasil maka akan dilanjutkan 