import os
import Train
def main():
    for file in os.listdir("B:/MP/Cars"):
        print(str(file))
        Train.Train_Data(str(file))

if __name__ == "__main__":
    main()