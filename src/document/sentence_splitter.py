SECTION_CHUNK_SIZES = {
    # Wiki (answer-critical)
    "lead_section": 500,        
    "plot_setup": 400,          
    "plot_build_up": 450,       
    "plot_ending": 300,         
    "production": 500,          
    "reception": 500,           

    # IMDb (fact-heavy)
    "synopsis": 450,            
    "summaries": 450,           
    "trivia": 300,              
    "goofs_continuity": 300,    
    "goofs_factual": 300,       

    # Combined
    "awards_finance": 600,      
}


SECTION_CHUNK_OVERLAP = {
    "lead_section": 0.10,

    "plot_setup": 0.15,
    "plot_build_up": 0.15,
    "plot_ending": 0.20,   

    "synopsis": 0.15,
    "summaries": 0.15,

    "trivia": 0.05,
    "goofs_continuity": 0.05,
    "goofs_factual": 0.05,

    "production": 0.10,
    "reception": 0.10,

    "awards_finance": 0.10,
}


DEFAULT_OVERLAP = 0.10


def get_chunk_size(section: str) -> int:
    return SECTION_CHUNK_SIZES.get(section, 800)


def get_overlap_chars(section: str, chunk_size: int) -> int:
    pct = SECTION_CHUNK_OVERLAP.get(section, DEFAULT_OVERLAP)
    return int(chunk_size * pct)
