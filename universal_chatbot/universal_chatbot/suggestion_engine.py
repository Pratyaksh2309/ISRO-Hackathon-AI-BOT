from kg_builder import graph

def suggest_questions():
    result = graph.run("""
        MATCH (s)-[r]->(o)
        RETURN DISTINCT type(r) AS relation
        LIMIT 10
    """).data()
    return [f"What is the {r['relation'].replace('_',' ').lower()} of X?" for r in result]