#!/bin/bash
ollama pull qwen3.6
ollama launch claude --model qwen3.6

ollama pull gpt-oss:120b
ollama launch claude --model gpt-oss:120b