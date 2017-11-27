from time import sleep
while True:
    try:
        for i in range(1, 5):
            print(str(5 - i) + " seconds remain", flush=True)
            sleep(1)

        print("complete")
        break
    except KeyboardInterrupt:
        print("retrying")
