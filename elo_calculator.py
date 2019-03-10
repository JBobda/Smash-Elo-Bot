def calculate_elo(k, winner_score, loser_score):
    prob_one, prob_two = get_elo_probability(winner_score, loser_score)

    new_winner_score = round(winner_score + k*(1 - prob_one))
    new_loser_score = round(loser_score + k*(0 - prob_two))

    return new_winner_score, new_loser_score

def get_elo_probability(rating_one, rating_two):
    probability_r2 = (1.0/(1.0 + pow(10, ((rating_one - rating_two)/400))))
    probability_r1 = (1.0/(1.0 + pow(10, ((rating_two - rating_one)/400))))

    return probability_r1,probability_r2

if __name__ == "__main__":
    print(calculate_elo(30, 1200, 1000))