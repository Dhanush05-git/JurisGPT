import re

def chunk_text(text: str):
    # 1. Split Constitution Articles.
    article_chunks = re.split(r'\n(?=Article\s+\d+)', text)

    final_chunks = []

    for chunk in article_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # 2. Split IPC Sections.
        ipc_sections = re.split(r'\n(?=Section\s+\d+)', chunk)

        for sec in ipc_sections:
            sec = sec.strip()
            if not sec:
                continue

            # 3. Split BNS Sections.
            bns_sections = re.split(r'\n(?=BNS\s+Section\s+\d+)', sec)

            for bns in bns_sections:
                bns = bns.strip()
                if bns:
                    final_chunks.append(bns)

    return final_chunks
