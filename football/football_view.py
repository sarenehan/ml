from database import DBSession

schema = """
create view football_view AS

select Description,
	--79 is the average qb rating
	coalesce(QBR, 55) * IsPass as Pass_Score,
	--55 is the average completion percentage
	coalesce(quarterback."Cmp%", 55) * IsPass as Completion_Percentage,
	-- 4.9 is the average td percentage
	coalesce(quarterback."TD%", 4.9) * IsPass as TD_Percentage,
	-- 7.24 is the average yards per attempt
	coalesce(quarterback."Y/A", 7.24) * IsPass as Yard_Per_Attempt,
	-- 11.6 is the average yards per catch
	coalesce(quarterback."Y/C", 11.6) * IsPass as Yards_Per_Catch,
	--4.07 is the average yards per attempt for rbs with at least 30 carries
	CASE when IsRush = 0
		THEN 0
	WHEN COALESCE(running_back.Att, 0) < 30
		THEN 4.07
	ELSE
		coalesce(running_back."Y/A", 4.07)
	END as Rush_Score,
	Yards,
	IsRush,
	IsPass,
	Down,
	Formation,
	PassType,
	PlayType,
	SeriesFirstDown,
	ToGo,
	YardLine,
	YardLineFixed,
	coalesce(defense."Y/P", 5.43) as Yard_Per_Play


from football
left join quarterback on (
	(lower(football.Description) like '%'||lower(
		substr(quarterback.First_Name, 1, 1))||'.'
		||lower(quarterback.Last_Name)||'%') = 1
	and football.IsPass = 1
)
left join running_back on (
	(lower(football.Description) like '%'||lower(
		substr(running_back.First_Name, 1, 1))||'.'
		||lower(running_back.Last_Name)||'%') = 1
	and football.IsRush = 1
)
left join defense on (
	football.DefenseTeam = defense.Team_Abbr
)

where IsChallengeReversed != 1
and IsInterception != 1
and IsFumble != 1
and (IsPenalty and IsPenaltyAccepted) != 1
and IsNoPlay != 1
and Description != 'TWO-MINUTE WARNING'
and IsTwoPointConversion != 1
and PlayType != 'KICK OFF'
and PlayType != 'PUNT'
and PlayType != 'TIMEOUT'
and PlayType is not null
and PlayType != 'EXTRA POINT'
and PlayType != 'FIELD GOAL'
and PlayType != 'NO PLAY'
and PlayType != 'QB KNEEL'
and PlayType != 'EXCEPTION'
and PlayType != 'CLOCK STOP'
and PlayType != 'PENALTY'

group by Description;
"""

if __name__ == '__main__':
	DBSession.query('drop view if exists football_view')
	DBSession.query(schema)
