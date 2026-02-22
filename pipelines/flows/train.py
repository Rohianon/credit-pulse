"""Train the credit scoring model."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.services.credit_model import train_and_evaluate

if __name__ == "__main__":
    train_and_evaluate()
