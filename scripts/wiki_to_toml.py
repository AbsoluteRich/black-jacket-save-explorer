# Obtained from https://blackjacket.wiki.gg/wiki/User:Dragod/ID
data = """
Wild Card 	Wild Card 	c510fa71-4ad5-4457-b352-e6c0ba902ac0 	✅
Lucky Charm 	Lucky Charm 	e36a78cc-e6ca-40d9-bbe1-0bd6cdecdc37 	❌
Wide Table 	Wide Table 	0563c780-5163-4a4c-aaaf-e6848d855f47 	❌
Wide Sleeve 	Wide Sleeve 	6268a143-f1cb-40ec-bbb5-b904fcfdacce 	✅
Coin String 	Coin String 	7a3224c1-ea57-4689-ab74-8cf52323ac8f 	✅
Big Pot 	Big Pot 	7b6b570e-12d0-4038-acbc-18f7f13311b5 	✅
Marble Eye 	Marble Eye 	cd9e2c5c-3928-4ddd-b118-735fbe74bfd3 	❌
Shackles 	Shackles 	af9b3b98-c563-4b9f-a46c-98c3380a5cab 	✅
Lucky Find 	Lucky Find 	fc1d6aec-d1d2-4d78-8891-b88eb68a80c1 	✅
Safety Pin 	Safety Pin 	3dae5e5b-8e65-48b2-b4a6-163847993861 	✅
(Will activate until the score is 21, or all the Safety Pins are used.)
Infused Glyph 	Infused Glyph 	2c3b76cb-6a53-4287-8ef0-ce89cc3e9b7d 	❌
Box of Matches 	Box of Matches 	9fe31180-50c5-486d-ad07-61159d95342f 	❌
Magnifying Glass 	Magnifying Glass 	aa314d85-1b93-4627-af0a-f050e02323db 	❌
Dagger 	Dagger 	a8058435-1862-411e-a3aa-97db806503c2 	✅
Intense Flames 	Intense Flames 	a964231a-2899-4c07-afdd-a6fc529a420b 	✅
Vines 	Vines 	5727e4ea-62ac-48b0-94a6-c3360f3e3134 	✅
Lost Finger 	Lost Finger 	0368670f-cc23-4dc4-a8aa-447b3d8ee290 	✅
Propagation 	Propagation 	b2cbe625-7da0-4e38-9e6b-42ee7d47c15a 	❌
(Gameplay becomes frozen)
Sharpened Tool 	Sharpened Tool 	9b78e5c0-f6ec-48e0-b2be-37ad8952cc15 	✅
Brute's Grasp 	Brute's Grasp 	7efd83cd-f7d2-4088-85d1-3a83278f4fcf 	✅
Compulsive All-In 	Compulsive All-In 	6da7e760-9fb3-432e-a186-baf61f88e690 	✅
Compulsive Dare 	Compulsive Dare 	5aaf4d0d-127c-4de0-b224-d2a5c21ba25d 	✅
Compulsive Wish 	Compulsive Wish 	f67198a3-5763-4a68-af18-a229dc419f04 	✅
Heart Cards 	Heart Cards 	425015d3-4008-47b3-bf5e-c5da2d43e8ff 	❌
Diamond Cards 	Diamond Cards 	1fdc315a-2b23-487b-93cf-ee8ead802c9d 	❌
Spade Cards 	Spade Cards 	e2882bd2-8802-418f-ada3-af788007ebec 	❌
Clubs Cards 	Clubs Cards 	0e223f3e-0f09-4547-a6f2-c74270a917dd 	❌
Flame Cards 	Flame Cards 	445c6bc6-487a-4fc4-a616-334432567369 	❌
Greed Cards 	Greed Cards 	f101088c-d8df-453a-a861-0b5e34c56b59 	❌
Tumor Cards 	Tumor Cards 	a118090a-0e5e-4d69-b8bd-c1858d36ffae 	❌
Teeth Cards 	Teeth Cards 	6f51dcd1-877c-4983-a107-3ea3edc22b5d 	❌
The Royals 	The Royals 	9d267919-6c71-4b66-b305-a1aa89db996c 	❌
The Vice 	The Vice 	4f7d6355-e137-47a0-92ca-0bda7501c642 	❌
The Shame 	The Shame 	b590b6bd-f3fe-4c20-bdce-de74b70381c4 	❌
The Family 	The Family 	6a96941e-c88d-42af-882b-fcd2359b193a 	❌
Train Set 	Train Set 	7dddc0aa-4218-47b9-ae80-c9e512fd20b7 	❌
Abyssal Doom 	Abyssal Doom 	bda31940-0837-4506-8328-ef0680fce21f 	❌
Flaming Souls 	Flaming Souls 	295e2fb1-5843-4fb5-99a1-a740f0aba817 	❌
Thin Air 	Thin Air 	6cabf8d6-c768-4937-b3ae-307e239ebf30 	❌
Zen 	Zen 	123386ce-cb8d-470c-b373-febd9cac236f 	✅
Haze 	Haze 	d8bcd891-88cf-4a6e-bb68-f0757dc816b9 	❌
Tattered Table 	Tattered Table 	156afa21-e62a-4521-85ff-e7dc89413f17 	❌
Bell Chimes 	Bell Chimes 	b45e55d0-0869-49a4-bf86-164f405c7fc6 	✅
Furnace 	Furnace 	604aacf6-26da-4522-9147-a68d07b9dca9 	✅ 
"""

if __name__ == "__main__":
    processed = []

    for line in data.splitlines():
        line = line.split("\t")
        try:
            processed.append((line[1].strip(), line[2].strip(), line[3]))
            print(processed[-1])
        except IndexError:
            pass

    assert len(processed) == 45 - 1
    longest_length = max(len(artefact[0]) for artefact in processed)

    print()
    for artefact in processed:
        print(f"{artefact[0].rjust(longest_length)}\t{artefact[1]}\t{artefact[2]}")
    print()

    for artefact in processed:
        print(f'{artefact[1]} = "{artefact[0]}"')
