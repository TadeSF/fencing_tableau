export interface UserData {
    id: string;
    name: string;
    club: string;
    nationality: string;
    start_number: number;
    allow_fencers_to_start_matches: boolean;
    allow_fencers_to_input_scores: boolean;
    allow_fencers_to_referee: boolean;
    gender: string;
    age: number;
    handedness: string;
    approved_tableau: boolean;
    next_matches: MatchData[];
    outcome_last_matches: MatchData[];
    last_matches: MatchData[];
    current_rank: number;
    group: number;
    current_group_rank: number;
    group_stage: boolean;
    statistics: StatisticsData;
    win_percentage: number;
    points_difference: number;
    points_per_match: number;
    graph_data: GraphData;
    num_fencers: number;
}

export interface MatchData {
    id: string;
    piste: number;
    piste_occupied: boolean;
    color: "green" | "red";
    ongoing: boolean;
    opponent: FencerData;
}

export interface FencerData {
    id: string;
    name: string;
    club: string;
    nationality: string;
    current_rank: number;
    current_group_rank: number;
    last_matches: any[];
}

export interface StatisticsData {
    preliminary_round: SingleStatisticsData[];
    elimination: SingleStatisticsData;
    overall: SingleStatisticsData;
}

export interface SingleStatisticsData {
    matches: number;
    wins: number;
    losses: number;
    points_for: number;
    points_against: number;
}

export interface GraphData {
    standings: {
        labels: string[];
        data: number[];
        y_max: number;
    };
    points_difference: {
        labels: string[];
        data: number[];
    };
    points_difference_per_match: {
        "data": number[];
    };
}

