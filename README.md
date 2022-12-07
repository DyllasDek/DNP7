# DNP7
DNP7 Lab RAFT protocol with Anna Kopeikina 

## Issues 
There is one interesting bug (apparently due to thread), which can lead to the fact that even after the server is disconnected, it is necessary to send a deathbed election and can become a leader before death, even if it was not

> I am a candidate. Term: 3  
> I am a follower. Term: 3  
> Voted for node 1  
> Voted for node 2  
> Shutting down  
> The leader is dead  
> I am a candidate. Term: 6  
> Votes received  
> I am a leader. Term: 6  
> *dead*  
