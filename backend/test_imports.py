import openai
import google.generativeai as genai
import torch
from transformers import AutoModel, AutoTokenizer
import magic
import docx
import PyPDF2
import unstructured
from unstructured.partition.auto import partition
import langdetect
import bs4
import chardet
import emoji
import html5lib
import psutil
import iso639
import oxmsg
import rapidfuzz

print("All packages imported successfully!") 