import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pimeyes_integration.pimeyes_api_wrapper import search_face
from meta_glasses_integration.meta_glasses_interface import display_ar_overlay

def main():
    print("UNIVERSAL_PLATFORM_INITIALIZED")

if __name__ == "__main__":
    main()
