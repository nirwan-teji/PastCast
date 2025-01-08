import base64
from django.shortcuts import render
from .forms import ImageUploadForm
from groq import Groq
import os

def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['image']
            image_path = f"/tmp/{image.name}"
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            base64_image = convert_image_to_base64(image_path)
            base64_image_url = f"data:image/jpeg;base64,{base64_image}"
            api_key = "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"
            os.environ["GROQ_API_KEY"] = api_key

            client = Groq()
            completion = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are an expert in history and cultural anthropology. I will provide you with an image of a historical monument, artifact, or cultural symbol. Your task is to analyze the image and provide detailed insights divided into the following sections: 1) Name and Identification: Clearly identify the monument, artifact, or cultural symbol in the image. If uncertain, provide the closest matches or possibilities. 2) Historical Background: Describe the origin, time period, and context in which it was created. Include information about the civilization, era, or people associated with it. 3) Cultural Significance: Explain the significance of this monument or artifact in the cultural, spiritual, or societal context of its time. Highlight any rituals, practices, or values associated with it. 4) Architectural/Design Details (if applicable): Provide a description of its architectural style, design elements, materials used, and unique features that make it stand out. 5) Current Relevance: Discuss how this monument or artifact is perceived today. Mention if it is a UNESCO World Heritage site, a popular tourist destination, or holds any special importance in modern society. Ensure your answer is precise, easy to understand, and includes only verified information. Avoid speculation unless explicitly stated as such. dont add texts like(if applicable) or (optional) in the answer. " },
                            {   "type": "image_url",
                                "image_url": {
                                    "url": base64_image_url
                                }
                            }
                        ]
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )

            response = completion.choices[0].message.content if completion.choices and completion.choices[0].message else "No message content received."
            return render(request, 'result.html', {'response': response})
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})