candidatos = [
    {"candidato": "João Silva", "partido": "Partido do Futuro"},
    {"candidato": "Maria Oliveira", "partido": "União Nacional"},
    {"candidato": "Carlos Souza", "partido": "Movimento Progressista"},
    {"candidato": "Ana Lima", "partido": "Aliança Popular"},
    {"candidato": "Pedro Rocha", "partido": "Democracia Real"}
]

votacoes = {}

while True:
    print("\nLista de candidatos:")
    for idx, cand in enumerate(candidatos, start=1):
        print(f"{idx} - Candidato: {cand['candidato']} | Partido: {cand['partido']}")

    try:
        escolha = int(input("Escolha o número do candidato que deseja votar (ou 0 para sair): ")) - 1

        if escolha == -1:
            print("Encerrando votação...")
            break  

        if 0 <= escolha < len(candidatos):
            verif = input("Deseja mesmo prosseguir? (s/n): ").strip().lower()
            if verif == 's':
                candidato_escolhido = candidatos[escolha]["candidato"]
                votacoes[candidato_escolhido] = votacoes.get(candidato_escolhido, 0) + 1
                print("Voto registrado com sucesso!")
            else:
                print("Votação cancelada.")
        else:
            print("Número inválido. Escolha um candidato da lista.")

    except ValueError:
        print("Entrada inválida. Digite um número.")

print("\nResultado da votação:")
if votacoes:
    for candidato, votos in votacoes.items():
        print(f"{candidato}: {votos} votos")
    vencedor = max(votacoes, key=votacoes.get) 
    print(f"\nO vencedor da eleição é: {vencedor} com {votacoes[vencedor]} votos!!")
else:
    print("Nenhum voto foi registrado.")

    