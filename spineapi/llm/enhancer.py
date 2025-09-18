"""
LLM Enhancement Module

Optional integration with Language Models to enhance generated code with better 
docstrings, error handling, and comments.
"""
from typing import Optional, Dict, Any

try:
    import openai
except ImportError:
    openai = None

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
except ImportError:
    AutoTokenizer = None
    AutoModelForCausalLM = None
    torch = None


class LLMEnhancer:
    """LLM-based code enhancement."""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        self._client = None
        self._tokenizer = None
        self._model_instance = None
        
        self._initialize_provider()
    
    def _initialize_provider(self) -> None:
        """Initialize the LLM provider."""
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "huggingface":
            self._initialize_huggingface()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _initialize_openai(self) -> None:
        """Initialize OpenAI client."""
        if openai is None:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        try:
            self._client = openai.OpenAI()
            self.model = self.model or "gpt-3.5-turbo"
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
    
    def _initialize_huggingface(self) -> None:
        """Initialize HuggingFace model."""
        if AutoTokenizer is None or AutoModelForCausalLM is None:
            raise ImportError("Transformers package not installed. Install with: pip install transformers torch")
        
        try:
            model_name = self.model or "microsoft/CodeGPT-small-py"
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model_instance = AutoModelForCausalLM.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize HuggingFace model: {e}")
    
    def enhance_code(
        self, 
        code: str, 
        file_type: str = "python", 
        context: str = ""
    ) -> Optional[str]:
        """
        Enhance code with better documentation and error handling.
        
        Args:
            code: Original code to enhance
            file_type: Type of code file (python, etc.)
            context: Additional context about the code
            
        Returns:
            Enhanced code or None if enhancement fails
        """
        try:
            if self.provider == "openai":
                return self._enhance_with_openai(code, file_type, context)
            elif self.provider == "huggingface":
                return self._enhance_with_huggingface(code, file_type, context)
        except Exception as e:
            # Don't fail the entire generation if LLM enhancement fails
            print(f"Warning: LLM enhancement failed: {e}")
            return None
    
    def _enhance_with_openai(self, code: str, file_type: str, context: str) -> Optional[str]:
        """Enhance code using OpenAI API."""
        prompt = f"""Please enhance the following {file_type} code by:
1. Adding comprehensive docstrings to all functions and classes
2. Improving error handling with try-catch blocks where appropriate
3. Adding inline comments for complex logic
4. Ensuring the code follows best practices
5. Keep the same functionality and structure

Context: {context}

Original code:
```{file_type}
{code}
```

Enhanced code:"""

        try:
            if self._client is None:
                return None
                
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software engineer. Enhance the provided code while maintaining its original functionality."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000,
            )
            
            enhanced_code = response.choices[0].message.content.strip()
            
            # Extract code from markdown if present
            if f"```{file_type}" in enhanced_code:
                start = enhanced_code.find(f"```{file_type}") + len(f"```{file_type}")
                end = enhanced_code.rfind("```")
                if end > start:
                    enhanced_code = enhanced_code[start:end].strip()
            
            return enhanced_code
            
        except Exception as e:
            print(f"OpenAI enhancement failed: {e}")
            return None
    
    def _enhance_with_huggingface(self, code: str, file_type: str, context: str) -> Optional[str]:
        """Enhance code using HuggingFace model."""
        # This is a simplified implementation
        # In practice, you'd want to fine-tune the model for code enhancement
        try:
            if self._tokenizer is None or self._model_instance is None or torch is None:
                return None
                
            prompt = f"# Enhanced {file_type} code\n{code}\n# Additional improvements:"
            
            inputs = self._tokenizer.encode(prompt, return_tensors="pt", max_length=1024, truncation=True)
            
            with torch.no_grad():
                outputs = self._model_instance.generate(
                    inputs,
                    max_length=inputs.shape[1] + 500,
                    temperature=0.1,
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id
                )
            
            enhanced_code = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the relevant part
            if prompt in enhanced_code:
                enhanced_code = enhanced_code[len(prompt):].strip()
            
            # For this demo, we'll just return the original code with a comment
            # In practice, you'd implement proper code enhancement logic
            return f"# Enhanced by HuggingFace model\n{code}"
            
        except Exception as e:
            print(f"HuggingFace enhancement failed: {e}")
            return None
    
    def generate_docstring(self, function_code: str) -> Optional[str]:
        """Generate a docstring for a function."""
        if self.provider == "openai" and self._client:
            prompt = f"""Generate a comprehensive docstring for this Python function:

```python
{function_code}
```

The docstring should include:
- Brief description
- Args section with type hints
- Returns section with type hints
- Raises section if applicable
- Example usage if helpful

Return only the docstring in triple quotes format:"""

            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Python developer. Generate clear, comprehensive docstrings."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500,
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"Docstring generation failed: {e}")
                return None
        
        return None
