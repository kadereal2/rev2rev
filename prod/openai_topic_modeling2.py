import os
import json
import re
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv('prod/config.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_topics(reviews, batch_size=10):
    """Extract meaningful topics from a list of reviews"""
    all_topics = []
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i + batch_size]
        reviews_text = "\n\n".join([f"Review {j+1}: {review}" for j, review in enumerate(batch)])
        
        prompt = f"""
        Analyze these app reviews and identify specific, actionable topics for product managers.
        For each topic:
        1. Be specific (e.g., avoid "UI issues")
        2. Focus on concrete problems
        3. Include examples from reviews
        Format each topic as:
        TOPIC: [Brief name]
        DESCRIPTION: [1-2 sentence description]
        IMPACT: [How this affects users]
        EVIDENCE: [Direct quotes from reviews]
        
        Reviews:
        {reviews_text}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert product analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        topic_text = response.choices[0].message.content.strip()
        batch_topics = [topic.strip() for topic in topic_text.split("\n\n") if topic.strip()]
        all_topics.extend(batch_topics)
    
    return all_topics

def consolidate_topics_fixed(topics_list, min_topics=8, max_topics=15):
    """Consolidate topics into a manageable number with emoji suggestions"""
    if not topics_list or len(topics_list) <= min_topics:
        return topics_list
    
    numbered_topics = [f"TOPIC {i}:\n{topic.strip()}" for i, topic in enumerate(topics_list, 1)]
    all_topics_text = "\n\n".join(numbered_topics)
    
    prompt = f"""
    Consolidate these {len(topics_list)} topics into {min_topics}-{max_topics} meaningful groups.
    For each group:
    - TITLE: [Brief, actionable title]
    - DESCRIPTION: [1-2 sentence description]
    - IMPACT: [How this affects users]
    - EVIDENCE: [Direct quotes from reviews]
    - EMOJI: [A single relevant emoji]
    Format as:
    TITLE: [Title]
    DESCRIPTION: [Description]
    IMPACT: [Impact]
    EVIDENCE: [Evidence]
    EMOJI: [Emoji]
    
    Topics:
    {all_topics_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a product analytics expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    consolidated_text = response.choices[0].message.content.strip()
    consolidated_topics = [f"TITLE: {topic.strip()}" for topic in re.split(r'\n\s*TITLE:\s*', consolidated_text) if topic.strip()]
    return consolidated_topics

def prioritize_topics(topics):
    """Prioritize topics based on impact, frequency, and business value"""
    if not topics:
        return []
    
    all_topics = "\n\n".join(topics)
    
    prompt = f"""
    Rank these topics by priority for a product team, based on:
    - User impact
    - Frequency
    - Business impact
    Format each as:
    PRIORITY: [HIGH/MEDIUM/LOW]
    TOPIC: [Title]
    DESCRIPTION: [Description]
    IMPACT: [Impact]
    EVIDENCE: [Evidence]
    
    Topics:
    {all_topics}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a product analytics expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    prioritized_text = response.choices[0].message.content.strip()
    prioritized_topics = [f"PRIORITY: {topic.strip()}" for topic in re.split(r'\n\s*PRIORITY:\s*', prioritized_text) if topic.strip()]
    return prioritized_topics

def associate_reviews_with_topics(reviews, topics):
    """Associate each review with the most relevant topic"""
    if not reviews or not topics:
        return {}
    
    review_topics = {}
    for review in reviews:
        best_match = None
        highest_score = -1
        
        for topic in topics:
            score = 0
            topic_lower = topic.lower()
            key_phrases = []
            
            for field in ['TITLE', 'DESCRIPTION', 'EVIDENCE']:
                match = re.search(rf'{field}:\s*(.*?)(?:\n|$)', topic)
                if match:
                    key_phrases.append(match.group(1).lower())
            
            review_lower = review.lower()
            for phrase in key_phrases:
                for word in phrase.split():
                    if len(word) > 3 and word in review_lower:
                        score += 1
            
            if score > highest_score:
                highest_score = score
                best_match = topic
        
        if best_match is None and topics:
            best_match = topics[0]
        
        review_topics[review] = best_match
    
    return review_topics

def calculate_topic_statistics(review_topics):
    """Calculate count and percentage for each topic"""
    if not review_topics:
        return {"total_reviews": 0, "topic_counts": {}, "topic_percentages": {}}
    
    topic_counts = {}
    for review, topic in review_topics.items():
        title = re.search(r'TITLE:\s*(.*?)(?:\n|$)', topic).group(1).strip()
        topic_counts[title] = topic_counts.get(title, 0) + 1
    
    total = len(review_topics)
    topic_percentages = {title: (count / total) * 100 for title, count in topic_counts.items()}
    
    return {
        "total_reviews": total,
        "topic_counts": topic_counts,
        "topic_percentages": topic_percentages
    }

def generate_executive_summary(prioritized_topics):
    """Generate a concise executive summary"""
    topics_text = "\n\n".join(prioritized_topics)
    
    prompt = f"""
    Create an executive summary for product managers based on these prioritized topics:
    {topics_text}
    
    Include:
    1. SUMMARY: 3-5 sentence overview
    2. KEY RECOMMENDED ACTIONS: Top 3 actions with:
       - Problem Statement
       - Business Impact
       - Recommended Action
       - Key Metrics to Follow
    Format as a professional markdown report with headings.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a product analytics director."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    
    return response.choices[0].message.content.strip()

def create_restructured_json(initial_topics, consolidated_topics, prioritized_topics, review_topics, topic_stats):
    """Create the final JSON structure with emojis"""
    topic_stats = topic_stats or {"total_reviews": 0, "topic_counts": {}, "topic_percentages": {}}
    
    processed_consolidated = []
    for topic in consolidated_topics:
        details = {}
        for field in ['TITLE', 'DESCRIPTION', 'IMPACT', 'EVIDENCE', 'EMOJI']:
            match = re.search(rf'{field}:\s*(.*?)(?:\n|$)', topic)
            details[field.lower()] = match.group(1).strip() if match else ""
        
        title = details["title"]
        count = topic_stats["topic_counts"].get(title, 0)
        percentage = topic_stats["topic_percentages"].get(title, 0.0)
        priority = "MEDIUM"  # Default, updated below
        emoji = details.get("emoji", "📦")  # Use suggested emoji or default
        
        for p_topic in prioritized_topics:
            p_title = re.search(r'TOPIC:\s*(.*?)(?:\n|$)', p_topic)
            if p_title and p_title.group(1).strip() == title:
                p_priority = re.search(r'PRIORITY:\s*([^\n]*)', p_topic)
                priority = p_priority.group(1).strip() if p_priority else "MEDIUM"
                break
        
        processed_consolidated.append({
            "title": title,
            "description": details["description"],
            "impact": details["impact"],
            "evidence": details["evidence"],
            "count": count,
            "percentage": percentage,
            "priority": priority,
            "emoji": emoji
        })
    
    return {
        "topic_modeling": {
            "extracted_topics": initial_topics,
            "consolidated_topics": processed_consolidated,
            "prioritized_topics": prioritized_topics,
            "executive_summary": generate_executive_summary(prioritized_topics)
        }
    }

def run_analysis(reviews, min_topics=8, max_topics=15):
    """Run the complete analysis workflow"""
    print(f"Analyzing {len(reviews)} reviews...")
    
    # Extract initial topics
    initial_topics = extract_topics(reviews)
    print(f"Extracted {len(initial_topics)} topics")
    
    # Consolidate topics with emoji suggestions
    consolidated_topics = consolidate_topics_fixed(initial_topics, min_topics, max_topics)
    print(f"Consolidated to {len(consolidated_topics)} topics")
    
    # Prioritize topics
    prioritized_topics = prioritize_topics(consolidated_topics)
    print(f"Prioritized topics")
    
    # Associate reviews with topics and calculate stats
    review_topics = associate_reviews_with_topics(reviews, consolidated_topics)
    topic_stats = calculate_topic_statistics(review_topics)
    print(f"Calculated statistics")
    
    # Create final JSON with emojis
    result = create_restructured_json(initial_topics, consolidated_topics, prioritized_topics, review_topics, topic_stats)
    print("Analysis complete")
    
    return result
