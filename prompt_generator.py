import random

class AIPromptGenerator:
    def __init__(self):
        self.styles = [
            "cyberpunk",
            "vaporwave",
            "retrowave",
            "synthwave",
            "futuristic",
            "neon-noir"
        ]
        
        self.subjects = [
            "android",
            "cyborg",
            "AI being",
            "digital entity",
            "holographic figure",
            "synthetic consciousness"
        ]
        
        self.environments = [
            "digital landscape",
            "virtual reality",
            "cyberspace",
            "data stream",
            "neural network",
            "quantum realm"
        ]
        
        self.moods = [
            "contemplative",
            "enigmatic",
            "ethereal",
            "mysterious",
            "transcendent",
            "surreal"
        ]
        
        self.lighting = [
            "neon glow",
            "holographic light",
            "digital aurora",
            "binary sunset",
            "quantum particles",
            "data streams"
        ]
        
        self.additional_elements = [
            "floating code fragments",
            "geometric patterns",
            "digital artifacts",
            "glitch effects",
            "matrix-like symbols",
            "energy fields"
        ]

    def generate_prompt(self):
        """Generate a cohesive AI-themed image prompt"""
        style = random.choice(self.styles)
        subject = random.choice(self.subjects)
        environment = random.choice(self.environments)
        mood = random.choice(self.moods)
        light = random.choice(self.lighting)
        element = random.choice(self.additional_elements)
        
        prompt = f"A {mood} {subject} in a {style} {environment}, illuminated by {light}, surrounded by {element}, ultra detailed, 8k resolution, hyperrealistic digital art"
        return prompt

    def generate_hashtags(self):
        """Generate relevant hashtags for the AI-themed content"""
        base_hashtags = [
            "AIart",
            "artificialintelligence",
            "digitalart",
            "aiartcommunity",
            "futuretech",
            "aiartwork",
            "deeplearning",
            "machinelearning",
            "digitalcreature",
            "aigenerated",
            "futuristic",
            "cyberpunk",
            "digitalworld",
            "aigenart",
            "aiartist"
        ]
        
        # Add some style-specific hashtags
        style_specific = random.sample([
            "cyberpunkart",
            "vaporwaveart",
            "synthwave",
            "retrowave",
            "scifiart",
            "conceptart",
            "digitalillustration",
            "futureart",
            "technofuturism",
            "cyberpunkstyle"
        ], 5)  # Select 5 random style-specific hashtags
        
        # Combine and shuffle hashtags
        all_hashtags = base_hashtags + style_specific
        random.shuffle(all_hashtags)
        
        return all_hashtags[:15]  # Return 15 hashtags to avoid overcrowding

def generate_content():
    """Generate both prompt and hashtags"""
    generator = AIPromptGenerator()
    prompt = generator.generate_prompt()
    hashtags = generator.generate_hashtags()
    
    return {
        'prompt': prompt,
        'hashtags': hashtags
    }