from agents import function_tool
from openai import OpenAI
import os
from typing import List, Dict

@function_tool
def analyze_pdf_images(images_data: str = None, file_path: str = None) -> str:
    """
    Analyze PDF page images using OpenAI vision API for content understanding.
    
    Args:
        images_data: JSON string containing array of image objects with 'page' and 'base64_image' fields
        file_path: Path to JSON file containing image data (alternative to images_data)
    
    Returns:
        Combined analysis of all PDF pages for organization purposes
    """
    try:
        import json
        
        # Parse the images data
        try:
            if file_path and os.path.exists(file_path):
                # Load from file
                with open(file_path, 'r') as f:
                    images = json.load(f)
            elif images_data:
                # Load from string parameter
                images = json.loads(images_data)
            else:
                return "Error: No image data provided. Specify either images_data or file_path."
        except (json.JSONDecodeError, FileNotFoundError) as e:
            return f"Error: Failed to load images data - {str(e)}"
        
        if not isinstance(images, list):
            return "Error: Images data must be an array of image objects."
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        vision_results = []
        for image_obj in images:
            if not isinstance(image_obj, dict) or 'page' not in image_obj or 'base64_image' not in image_obj:
                vision_results.append(f"Error: Invalid image object format for page {image_obj.get('page', 'unknown')}")
                continue
                
            page_num = image_obj['page']
            base64_image = image_obj['base64_image']
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Analyze this page from a PDF document. Extract key information, main topics, document type, and any important details that would help with file organization. Be concise but comprehensive."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                page_analysis = response.choices[0].message.content
                vision_results.append(f"Page {page_num}: {page_analysis}")
                
            except Exception as e:
                vision_results.append(f"Page {page_num}: Error analyzing page - {str(e)}")
        
        # Combine all page analyses
        combined_analysis = "\n\n".join(vision_results)
        
        return f"VISION ANALYSIS RESULTS:\n\n{combined_analysis}"
        
    except Exception as e:
        return f"Error in analyze_pdf_images: {str(e)}"