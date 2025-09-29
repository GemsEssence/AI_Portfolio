import argparse, sys
from src.pipeline.orchestrator import SafetyOrchestrator
from src.ui.terminal import print_event

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--age", type=int, default=16, help="User age for content filtering")
    args = p.parse_args()
    orch = SafetyOrchestrator(user_age=args.age)
    print("Type messages. Ctrl+C to exit.")
    while True:
        try:
            msg = input("You: ")
        except KeyboardInterrupt:
            print("\nBye")
            sys.exit(0)
        outputs = orch.step(msg)
        print_event(msg, outputs)
        print(f"Action: {outputs['action']}\n")

if __name__ == "__main__":
    main()
