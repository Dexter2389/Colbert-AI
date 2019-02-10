import chain

with open("/home/saurabh/Personal/Stuff/Next Tech Lab AP/LSSC/caption_para.txt") as f:
    text = f.read()

text_model = chain.Text(text, state_size=3)

file = open("/home/saurabh/Personal/Stuff/Next Tech Lab AP/LSSC/text3.txt", "w")

for j in range(200):
    print(" ")
    for i in range(1):
        output = text_model.make_short_sentence(max_chars=230, min_chars=70)
        txt = output + "\n"
        print(txt)

        file.write(txt)
file.close()
