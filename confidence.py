"""
Confidence Scoring Module
Calculates confidence scores for RAG responses
"""

from typing import List, Dict

def calculate_confidence(chunks: List[Dict]) -> Dict:
    """
    Calculate confidence score based on retrieval results
    
    Args:
        chunks: Retrieved chunks with similarity scores
        
    Returns:
        Dictionary with confidence metrics
    """
    if not chunks:
        return {
            'score': 0.0,
            'level': 'No Data',
            'explanation': 'No relevant information found'
        }
    
    # Get similarity scores (convert distance to similarity if needed)
    similarities = []
    for chunk in chunks:
        sim = chunk.get('similarity', 0)
        # If similarity is very low (distance metric), convert it
        # Distance of 0.004-0.006 should be HIGH similarity
        if sim < 0.1:  # It's a distance metric
            # Convert distance to similarity (inverse)
            similarity = 1 / (1 + sim * 100)  # Scale up distance
        else:
            similarity = sim
        similarities.append(similarity)
    
    # Calculate metrics
    avg_similarity = sum(similarities) / len(similarities)
    max_similarity = max(similarities)
    min_similarity = min(similarities)
    
    # Calculate confidence score (0-100)
    variance = sum((s - avg_similarity) ** 2 for s in similarities) / len(similarities)
    
    # Weighted score
    confidence_score = (
        (avg_similarity * 0.5) +   # Average similarity (50% weight)
        (max_similarity * 0.3) +    # Best match (30% weight)
        ((1 - variance) * 0.2)      # Consistency (20% weight)
    ) * 100
    
    # Determine confidence level
    if confidence_score >= 80:
        level = 'High'
        explanation = 'Strong match found in documents'
    elif confidence_score >= 60:
        level = 'Medium'
        explanation = 'Relevant information found'
    elif confidence_score >= 40:
        level = 'Low'
        explanation = 'Limited relevant information'
    else:
        level = 'Very Low'
        explanation = 'Answer may not be reliable'
    
    return {
        'score': round(confidence_score, 1),
        'level': level,
        'explanation': explanation,
        'details': {
            'avg_similarity': round(avg_similarity, 3),
            'max_similarity': round(max_similarity, 3),
            'min_similarity': round(min_similarity, 3),
            'num_sources': len(chunks)
        }
    }

def get_confidence_color(score: float) -> str:
    """
    Get color code based on confidence score
    
    Args:
        score: Confidence score (0-100)
        
    Returns:
        Color code (green, yellow, orange, red)
    """
    if score >= 80:
        return 'green'
    elif score >= 60:
        return 'yellow'
    elif score >= 40:
        return 'orange'
    else:
        return 'red'

# Test the module
if __name__ == "__main__":
    # Test with sample chunks
    test_chunks = [
        {'similarity': 0.85},
        {'similarity': 0.82},
        {'similarity': 0.78}
    ]
    
    confidence = calculate_confidence(test_chunks)
    
    print("Confidence Score Test:")
    print(f"Score: {confidence['score']}")
    print(f"Level: {confidence['level']}")
    print(f"Explanation: {confidence['explanation']}")
    print(f"Details: {confidence['details']}")
    print(f"Color: {get_confidence_color(confidence['score'])}")