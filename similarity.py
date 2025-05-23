import json
from pathlib import Path
from PIL import Image
import imagehash
import os
import re  # Add this import for regular expressions
import shutil

class JsonPromptManager:
    def __init__(self, json_path):
        self.json_path = json_path
        self.prompts = self._load_prompts()
        
    def _load_prompts(self):
        """Load prompts from JSON file"""
        with open(self.json_path, 'r') as f:
            return json.load(f)
    
    def get_chapter_prompts(self, chapter_key):
        """Get all prompts for a specific chapter"""
        if chapter_key not in self.prompts:
            raise ValueError(f"Chapter '{chapter_key}' not found in prompts")
        return self.prompts[chapter_key]
    
    def get_prompt_by_unique_name(self, chapter_key, unique_name):
        """Get prompt for a specific unique_name in a chapter"""
        chapter_prompts = self.get_chapter_prompts(chapter_key)
        for prompt in chapter_prompts:
            if prompt["unique_name"] == unique_name:
                return prompt
        raise ValueError(f"Unique name '{unique_name}' not found in chapter '{chapter_key}'")

class ImageSelector:
    def __init__(self):
        pass
        
    def get_image_similarity_score(self, image_path, reference_image_path):
        """Calculate similarity score between two images using perceptual hash"""
        # Load images
        img1 = Image.open(image_path)
        img2 = Image.open(reference_image_path)
        
        # Calculate perceptual hashes
        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)
        
        # Calculate similarity (0 = identical, higher = more different)
        similarity = hash1 - hash2
        
        # Convert to similarity score (0 to 1, where 1 is most similar)
        max_possible_difference = 64  # Maximum possible difference for 8x8 hash
        similarity_score = 1 - (similarity / max_possible_difference)
        
        return similarity_score
    
    def find_matching_images(self, directory, base_filename):
        """Find all images that match the base filename pattern"""
        # Create pattern for matching filenames
        pattern = re.compile(f"{base_filename}(?:_[2-4])?\.jpg$")
        
        # Get all matching files
        matching_files = []
        for file in Path(directory).glob("*.jpg"):
            if pattern.match(file.name):
                matching_files.append(file)
        
        return sorted(matching_files)
    
    def select_best_image(self, image_dir, unique_name):
        """Select the best image from existing images in a directory"""
        # Find all matching images
        image_files = self.find_matching_images(image_dir, unique_name)
        
        if not image_files:
            raise ValueError(f"No matching images found for pattern: {unique_name}")
            
        print(f"Found {len(image_files)} matching images:")
        for img in image_files:
            print(f"- {img.name}")
        
        # Calculate similarity scores for each image
        scores = []
        for img_path in image_files:
            try:
                # Calculate average similarity with all other images
                total_similarity = 0
                comparison_count = 0
                
                for other_img in image_files:
                    if other_img != img_path:
                        score = self.get_image_similarity_score(str(img_path), str(other_img))
                        total_similarity += score
                        comparison_count += 1
                
                # Calculate average similarity
                avg_similarity = total_similarity / comparison_count if comparison_count > 0 else 0
                scores.append((img_path, avg_similarity))
                print(f"Image: {img_path.name}, Average Similarity Score: {avg_similarity:.4f}")
            except Exception as e:
                print(f"Error processing {img_path}: {str(e)}")
        
        if not scores:
            raise ValueError("No valid images could be processed")
        
        # Sort by similarity score in descending order
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best image path and its score
        best_image_path = scores[0][0]
        best_score = scores[0][1]
        
        return str(best_image_path), best_score

def main():
    # Initialize managers
    prompt_manager = JsonPromptManager("prompts/video10.json")
    image_selector = ImageSelector()
    
    # Get all prompts for chapter 6
    chapter_prompts = prompt_manager.get_chapter_prompts("chapter_6")
    
    # Process each prompt
    for prompt_data in chapter_prompts:
        unique_name = prompt_data["unique_name"]
        # prompt = prompt_data["prompt"]
        
        print(f"\nProcessing: {unique_name}")
        # print(f"Prompt: {prompt}")
        
        # Path to images
        image_dir = Path("images/video10/ch6")
        temp_dir = image_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            best_image, score = image_selector.select_best_image(str(image_dir), unique_name)
            print(f"Best matching image: {best_image}")
            print(f"Similarity score: {score:.4f}")
            
            # Move non-selected images to temp folder
            best_image_path = Path(best_image)
            for img_path in image_dir.glob(f"{unique_name}*.jpg"):
                if img_path.name != best_image_path.name:
                    temp_path = temp_dir / img_path.name
                    shutil.move(str(img_path), str(temp_path))
                    print(f"Moved {img_path.name} to temp folder")
            
        except Exception as e:
            print(f"Error processing {unique_name}: {str(e)}")

if __name__ == "__main__":
    main() 