class UndoablePartyElection(UndoableCandidatesElection,Undoable):
    def __init__(self,algorithm,candidates,maxPartySize):
        """
        constructs all possible parties up to maxPartySize
        """
        UndoableCandidatesElection.__init__(self,algorithm,candidates,["_alg","_candidates","_parties"])

        self._parties = []
        for i in range(1,maxPartySize+1):
            ##create all possible parties of size i
            itr = subsets.MonosizeLexIterator(i,len(self._candidates))
            while(itr.hasNext()):
                party = tuple([candidates[candidateIndex] for candidateIndex in itr.next()])
                self._parties.append((-self._alg.getContributionOf(party),party))
        heapify(self._parties)
        
        #self._acceptNext = UndoablePartyElection.acceptNext1
        
    def favorCandidate(self,cand):
        UndoableCandidatesElection.favorCandidate(self,cand)
        ##update parties' contributions
        ##preserve only parties that are distinct to members
        renewedParties = []
        for pInfo in self._parties:
            if cand not in pInfo[1]:
                renewedParties.append((-self._alg.getContributionOf(pInfo[1]),pInfo[1]))
        self._parties = renewedParties
        heapify(self._parties)
        
    def rejectLargeParties(self,maxSize):
        renewedParties = []
        for pInfo in self._parties:
            if  len(pInfo[1]) <= maxSize:
                renewedParties.append(pInfo)
        self._parties = renewedParties
        heapify(self._parties)
        
    def constructGreedySet(self,size):
        i = len(self._alg.getMembers())
        while(i<size):
            self.rejectLargeParties(size-i)
            self.acceptNext()
            i = len(self._alg.getMembers())
        return self.getResult()

    def getBestParty(self):
        """()->(-GB,(x1,x2...))"""
        vInfo = self._parties[0]
        return vInfo

    def getBestKParties(self,k):
        """
        ()->[(-GB1,(x11,x12...)),(-GB2,(x23,x24,..)),...]
        returns best k *disjoint* parties
        """
        result = []        
        bigParty = set([])
        tmpParties = copy.deepcopy(self._parties)
        l = len(bigParty)
        while (l<k):
            p = heappop(tmpParties)
            if (len(bigParty.intersection(p[1]))==0) and (len(p[1])+l <= k):
                bigParty.update(p[1])
                result.append(p)
                l=len(bigParty)
        return result

    #def setAcceptNext(self,function):
        #self._acceptNext = function
    
    #def acceptNext(self):
        #self._acceptNext(self)
        
    #def acceptNext1(self):
        ###add the best candidate to the group
        #cInfo = heappop(self._candidates)        
        #self.favorCandidate(cInfo[1])

    #def acceptNext2(self):
        ###add the best candidate to the group
        #pInfo = heappop(self._parties)        
        #for c in pInfo[1]:
            #self.favorCandidate(c)
            
        
