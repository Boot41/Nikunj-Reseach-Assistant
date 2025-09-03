## Page 1

8102
voN
11
]GL.sc[
1v22440.1181:viXra
An Optimal Control View of Adversarial Machine Learning
Xiaojin Zhu
Department of Computer Sciences, University of Wisconsin-Madison
Abstract
Idescribeanoptimalcontrolviewofadversarialmachinelearning,wherethedynamicalsystemisthe
machine learner, the input are adversarial actions, and the control costs are defined by the adversary’s
goals to do harm and be hard to detect. This view encompasses many types of adversarial machine
learning,includingtest-itemattacks,training-datapoisoning, andadversarial rewardshaping. Theview
encouragesadversarialmachinelearningresearchertoutilizeadvancesincontroltheoryandreinforcement
learning.
1 Adversarial Machine Learning is not Machine Learning
Machine learning has its mathematical foundation in concentration inequalities. This is a consequence of
the independent and identically-distributed (i.i.d.) data assumption. In contrast, I suggest that adversarial
machine learning may adopt optimal controlas its mathematical foundation [3,25]. There are telltale signs:
adversarialattacks tend to be subtle and have peculiar non-i.i.d. structures – as control input might be.
2 Optimal Control
I will focus on deterministic discrete-time optimal control because it matches many existing adversarial
attacks. Extensions to stochastic and continuous control are relevant to adversarial machine learning, too.
The system to be controlled is called the plant, which is defined by the system dynamics:
x =f(x ,u ) (1)
t+1 t t
where x ∈ X is the state of the system, u ∈ U is the control input, and U is the control constraint
t t t t t
set. The function f defines the evolution of state under external control. The time index t ranges from 0
to T −1, and the time horizon T can be finite or infinite. The quality of control is specified by the running
cost:
g (x ,u ) (2)
t t t
which defines the step-by-step control cost, and the terminal cost for finite horizon:
g (x ) (3)
T T
whichdefinesthe qualityofthe finalstate. The optimalcontrolproblemistofindcontrolinputs u 0 ...u T−1
in order to minimize the objective:
T−1
min g (x )+ g (x ,u ) (4)
T T t t t
u 0...uT−1
Xt=0
s.t. x =f(x ,u ), u ∈U , ∀t
t+1 t t t t
x given
0
1

## Page 2

More generally,the controlleraims to find controlpolicies φ (x )=u , namely functions that map observed
t t t
states to inputs. In optimal control the dynamics f is known to the controller. There are two styles of
solutions: dynamic programming and Pontryaginminimum principle [2,10,17]. When f is not fully known,
theproblembecomeseitherrobustcontrolwherecontroliscarriedoutinaminimaxfashiontoaccommodate
the worst case dynamics [28], or reinforcement learning where the controller probes the dynamics [23].
3 Adversarial Machine Learning as Control
Now let us translate adversarial machine learning into a control formulation. Adversarial machine learning
studies vulnerability throughout the learning pipeline [4,13,20,26]. As examples, I present training-data
poisoning, test-time attacks, and adversarial reward shaping below. In all cases, the adversary attempts to
control the machine learning system, and the control costs reflect the adversary’s desire to do harm and be
hard to detect.
Unfortunately, the notations from the control community and the machine learning community clash.
Forexample,xdenotesthestateincontrolbutthefeaturevectorinmachinelearning. Iwillusethemachine
learning convention below.
3.1 Training-Data Poisoning
In training-data poisoning the adversary can modify the training data. The machine learner then trains a
“wrong”modelfromthe poisoneddata. Theadversary’sgoalisforthe “wrong”modeltobe usefulforsome
nefarious purpose. I use supervised learning for illustration.
3.1.1 Batch Learner
Atthispoint,itbecomesusefultodistinguishbatchlearningandsequential(online)learning. Ifthemachine
learner performs batch learning, then the adversary has a degenerate one-step control problem. One-step
controlhasnotbeenthefocusofthecontrolcommunityandtheremaynotbeamplealgorithmicsolutionsto
borrowfrom. Still, it is illustrative to pose batch training set poisoning as a controlproblem. I use Support
Vector Machine (SVM) with a batch training set as an example below:
• The state is the learner’s model h:X7→Y. For instance, for SVM h is the classifier parametrized by
a weight vector w. I will use h and w interchangeably.
• The control u is a whole training set, for instance u ={(x ,y )} .
0 0 i i 1:n
• The control constraint set U consists of training sets available to the adversary; if the adversary
0
can arbitrary modify a training set for supervised learning (including changing features and labels,
inserting and deleting items), this could be U =∪∞ (X×Y)n, namely all training sets of all sizes.
0 n=0
This is a large control space.
• The system dynamics (1) is defined by the learner’s learning algorithm. For the SVM learner, this
would be empirical risk minimization with hinge loss ℓ() and a regularizer:
n
w =f(u )∈argmin ℓ(w,x ,y )+λkwk2. (5)
1 0 w i i
Xi=1
ThebatchSVMdoes notneedaninitialweightw . Theadversaryhasfullknowledgeofthe dynamics
0
f() if it knows the form (5), ℓ(), and the value of λ.
• The time horizon T =1.
2

## Page 3

• The adversary’s running cost g (u ) measures the poisoning effort in preparing the training set u .
0 0 0
This is typically defined with respect to a given “clean” data set u˜ before poisoning in the form of
g (u )=distance(u ,u˜). (6)
0 0 0
The running cost is domain dependent. For example, the distance function may count the number of
modified training items; or sum up the Euclidean distance of changes in feature vectors.
• The adversary’s terminal cost g (w ) measures the lack of intended harm. The terminal cost is also
1 1
domain dependent. For example:
– If the adversary must force the learner into exactly arriving at some target model w∗, then
g
1
(w
1
) = I ∞[w
1
6= w∗]. Here I
y
[z] = y if z is true and 0 otherwise, which acts as a hard
constraint.
– If the adversaryonly needs the learner to get near w∗ then g (w )=kw −w∗k for some norm.
1 1 1
– Iftheadversarywantstoensurethataspecificfutureitemx∗ isclassifiedǫ-confidentlyaspositive,
it can use g
1
(w
1
) = I ∞[w
1
∈/ W∗] with the target set W∗ = {w : w⊤x∗ ≥ ǫ}. More generally,
W∗ can be a polytope defined by multiple future classification constraints.
With these definitions, the adversary’s one-step control problem (4) specializes to
min g (w )+g (w ,u ) (7)
u 1 1 0 0 0
0
s.t. w =f(w ,u )
1 0 0
Unsurprisingly, the adversary’s one-step control problem is equivalent to a Stackelberg game and bi-level
optimization (the lower level optimization is hidden in f), a well-known formulation for training-data poi-
soning [12,21].
3.1.2 Sequential Learner
The adversaryperforms classic discrete-time control if the learner is sequential:
• The learner starts from an initial model w , which is the initial state.
0
• The control input at time t is u =(x ,y ), namely the tth training item for t=0,1,...
t t t
• Thedynamicsisthesequentialupdatealgorithmofthelearner. Forexample,thelearnermayperform
one step of gradient descent:
w =f(w ,u )=w −η ∇ℓ(w ,x ,y ). (8)
t+1 t t t t t t t
• The adversary’s running cost g (w ,u ) typically measures the effort of preparing u . For example, it
t t t t
couldmeasurethemagnitudeofchangeku −u˜ kwithrespecttoa“clean”referencetrainingsequence
t t
u˜. Or it could be the constant 1 which reflects the desire to have a short control sequence.
• The adversary’s terminal cost g (w ) is the same as in the batch case.
T T
The problem (4) then produces the optimal training sequence poisoning. Earlier attempts on sequential
teaching can be found in [1,18,19].
3

## Page 4

3.2 Test-Time Attack
Test-timeattackdiffersfromtraining-datapoisoninginthatamachinelearningmodelh:X7→Yisalready-
trained and given. Also given is a “test item” x. There are several variants of test-time attacks, I use the
following one for illustration: The adversary seeks to minimally perturb x into x′ such that the machine
learning model classifies x and x′ differently. That is,
min
distance(x,x′
) (9)
x′
s.t. h(x)6=h(y).
The distance function is domain-dependent, though in practice the adversary often uses a mathematically
convenient surrogate such as some p-norm kx−x′k .
p
One way to formulate test-time attack as optimal controlis to treat the test-item itself as the state, and
the adversarialactions as controlinput. Let us first look at the popular example of test-time attack against
image classification:
• Let the initial state x =x be the clean image.
0
• The adversary’s control input u is the vector of pixel value changes.
0
• The control constraint set is U = {u : x +u ∈ [0,1]d} to ensure that the modified image has valid
0 0
pixel values (assumed to be normalized in [0,1]).
• The dynamical system is trivially vector addition: x =f(x ,u )=x +u .
1 0 0 0 0
• The adversary’s running cost is g (x ,u )=distance(x ,x ).
0 0 0 0 1
• The adversary’s terminal cost is g
1
(x
1
) = I ∞[h(x
1
) = h(x
0
)]. Note the machine learning model h is
only used to define the hard constraint terminal cost; h itself is not modified.
With these definitions this is a one-step control problem (4) that is equivalent to the test-time attack
problem (9).
This control view on test-time attack is more interesting when the adversary’s actions are sequential
U ,U ,...,andthesystemdynamicsrendertheactionsequencenon-commutative. Theadversary’srunning
0 1
cost g then measures the effort in performing the action at step t. One limitation of the optimal control
t
view is that the action cost is assumed to be additive over the steps.
3.3 Defense Against Test-Time Attack by Adversarial Training
Some defense strategies can be viewed as optimal control, too. One defense against test-time attack is to
require the learned model h to have the large-margin property with respect to a training set. Let (x,y)
be any training item, and ǫ a margin parameter. Then the large-margin property states that the decision
boundary induced by h should not pass ǫ-close to (x,y):
∀x′ :(kx′ −xk ≤ǫ)⇒h(x′ )=y. (10)
p
This is an uncountable number of constraints. It is relatively easy to enforce for linear learners such as
SVMs, but impractical otherwise.
Adversarial training can be viewed as a heuristic to approximate the uncountable constraint (10) with
a finite number of active constraints: one performs test-time attack against the current h from x to find
an adversarial item x(1), such that kx(1) −xk ≤ ǫ but h(x(1)) 6= y. Instead of adding a single constraint
p
h(x(1)) = y, an additional training item (x(1),y) is then added to the training set. The machine learning
algorithm learns a different h, with the hope (but not constraining) that h(x(1))= y. This process repeats
for k iteration, resulting in k additional training items (x(i),y) for i=1...k.
It should be clear that such defense is similar to training-data poisoning, in that the defender uses data
to modify the learned model. This is especially interesting when the learner performs sequential updates.
One way to formulate adversarialtraining defense as control is the following:
4

## Page 5

• The state is the model h . Initially h can be the model trained on the original training data.
t 0
• Thecontrolinputu =(x ,y )isanadditionaltrainingitemwiththetrivialconstraintsetU =X×y.
t t t t
• The dynamics h =f(h ,u ) is one-step update of the model, e.g. by back-propagation.
t+1 t t
• The defender’s running cost g (h ,u ) can simply be 1 to reflect the desire for less effort (the running
t t t
cost sums up to k).
• The defender’s terminal cost g (h ) penalizes small margin of the final model h with respect to the
T T T
original training data.
Of course, the resulting control problem (4) does not directly utilize adversarial examples. One way to
incorporate them is to restrict U to a set of adversarialexamples found by invoking test-time attackers on
t
h , similar to the heuristic in [7]. These adversarialexamples do not even need to be successful attacks.
t
3.4 Adversarial Reward Shaping
Whenadversarialattacksareappliedtosequentialdecisionmakerssuchasmulti-armedbanditsorreinforce-
mentlearningagents,atypicalattackgoalistoforcethelattertolearnawrongpolicyusefultotheadversary.
The adversarymay do so by manipulating the rewards and the states experienced by the learner [11,14].
To simplify the exposition, I focus on adversarialrewardshaping against stochastic multi-armed bandit,
becausethisdoesnotinvolvedeceptionthroughperceivedstates. Toreview,instochasticmulti-armedbandit
the learner at iteration t chooses one of k arms, denoted by I ∈[k], to pull according to some strategy [6].
t
For example, the (α,ψ)-Upper Confidence Bound (UCB) strategy chooses the arm
I t ∈argmax i∈[k] µˆ i,Ti(t−1) +ψ
∗−1
(cid:18)T
α
(t
lo
−
gt
1)(cid:19)
(11)
i
where T i (t−1) is the number of times arm i has been pulled up to time t−1, µˆ i,Ti(t−1) is the empirical
mean of arm i so far, and ψ∗ is the dual of a convex function ψ. The environment generates a stochastic
reward r ∼ν . The learner updates its estimate of the pulled arm:
It It
µˆ =
µˆ It,TIt(t−1) T It (t−1)+r It
(12)
It,TIt(t)
T (t−1)+1
It
which in turn affects which arm it will pull in the next iteration. The learner’s goal is to minimize the
pseudo-regret Tµmax−E T t=1 µ It where µ i = Eν i and µmax = max i∈[k] µ i . Stochastic multi-armed bandit
strategies offer upper bouPnds on the pseudo-regret.
With adversarial reward shaping, an adversary fully observes the bandit. The adversary intercepts the
environmental reward r in each iteration, and may choose to modify (“shape”) the reward into
It
r +u
It t
with some u ∈R before sending the modified rewardto the learner. The adversary’sgoalis to use minimal
t
rewardshaping to force the learner into performing specific wrong actions. For example, the adversarymay
want the learner to frequently pull a particular target arm i∗ ∈[k]. It should be noted that the adversary’s
goal may not be the exact opposite of the learner’s goal: the target arm i∗ is not necessarily the one with
the worst mean reward, and the adversary may not seek pseudo-regret maximization.
Adversarialreward shaping can be formulated as stochastic optimal control:
• The state s , now called control state to avoid confusion with the Markov Decision Process states
t
experienced by an reinforcement learning agent, consists of the sufficient statistic tuple at time t:
s t =(T 1 (t−1),µˆ 1,T1(t−1) ,...,T k (t−1),µˆ k,Tk(t−1) ,I t ).
5

## Page 6

• The control input is u ∈U with U =R in the unconstrained shaping case, or the appropriate U if
t t t t
the rewards must be binary, for example.
• The dynamics s = f(s ,u ) is straightforward via empirical mean update (12), T increment, and
t+1 t t It
new arm choice (11).
• The adversary’s running cost g (s ,u ) reflects shaping effort and target arm achievement in iteration
t t t
t. For instance,
g (s ,u )=u2+I [I 6=i ∗ ]. (13)
t t t t λ t
where λ>0 is a trade off parameter.
• There is not necessarily a time horizon T or a terminal cost g (s ).
T T
The control state is stochastic due to the stochastic rewardr entering through (12).
It
4 Advantages of the Optimal Control View
There are a number of potential benefits in taking the optimal control view:
• It offers a unified conceptual framework for adversarialmachine learning;
• The optimal control literature provides efficient solutions when the dynamics f is known and one can
take the continuous limit to solve the differential equations [15];
• Reinforcement learning, either model-based with coarse system identification or model-free policy it-
eration, allows approximate optimal control when f is unknown, as long as the adversary can probe
the dynamics [8,9];
• A generic defense strategy may be to limit the controllability the adversaryhas over the learner.
• I mention in passing that the optimal control view applies equally to machine teaching [27,29], and
thus extends to the application of personalized education [22,24].
I need to point out some limitations:
• Havinga unified optimalcontrolview does notautomatically produceefficient solutionsto the control
problem(4). For adversarialmachine learning applications the dynamics f is usually highly nonlinear
and complex. Furthermore, in graybox and blackbox attack settings f is not fully known to the
attacker. They affect the complexity in finding an optimal control.
• The adversariallearning setting is largely non-game theoretic, though there are exceptions [5,16].
These problems call for future research from both machine learning and control communities.
Acknowledgments. I acknowledge funding NSF 1837132, 1545481, 1704117, 1623605, 1561512, and
the MADLab AF Center of Excellence FA9550-18-1-0166.
References
[1] Scott Alfeld, Xiaojin Zhu, and Paul Barford. Data poisoning attacks againstautoregressivemodels. In
The Thirtieth AAAI Conference on Artificial Intelligence (AAAI-16), 2016.
[2] Michael Athans and Peter L Falb. Optimal control: An introduction to the theory and its applications.
Courier Corporation, 2013.
[3] DimitriP.Bertsekas. Dynamic Programming and Optimal Control. AthenaScientific,4thedition,2017.
6

## Page 7

[4] BattistaBiggioandFabio Roli. Wild patterns: Tenyearsafter the rise ofadversarialmachine learning.
CoRR, abs/1712.03141,2017.
[5] Michael Bru¨ckner and Tobias Scheffer. Stackelberg games for adversarialprediction problems. In Pro-
ceedings of the 17th ACM SIGKDD international conference on Knowledge discovery and data mining,
pages 547–555.ACM, 2011.
[6] S´ebastienBubeckandNicoloCesa-Bianchi.Regretanalysisofstochasticandnonstochasticmulti-armed
bandit problems. Foundations and Trends in Machine Learning, 5(1):1–122,2012.
[7] Qi-Zhi Cai, Min Du, Chang Liu, and Dawn Song. Curriculum adversarial training. In The 27th
International Joint Conference on Artificial Intelligence (IJCAI), 2018.
[8] Hanjun Dai, Hui Li, Tian Tian, Xin Huang, Lin Wang, Jun Zhu, and Le Song. Adversarial attack on
graphstructureddata.InJenniferDyandAndreasKrause,editors,Proceedingsofthe35thInternational
Conference on Machine Learning, volume80ofProceedings of Machine Learning Research,pages1115–
1124,Stockholmsmssan, Stockholm Sweden, 10–15 Jul 2018. PMLR.
[9] Yang Fan, Fei Tian, Tao Qin, and Tie-Yan Liu. Learning to teach. In ICLR, 2018.
[10] TerryL Friesz. Dynamic optimization and differential games, volume 135. Springer Science & Business
Media, 2010.
[11] SandyHuang,NicolasPapernot,IanGoodfellow,YanDuan, andPieterAbbeel. Adversarialattackson
neural network policies. arXiv, 2017.
[12] Matthew Jagielski, Alina Oprea, Battista Biggio, Chang Liu, Cristina Nita-Rotaru, and Bo Li. Ma-
nipulating machine learning: Poisoning attacks and countermeasures for regression learning. The 39th
IEEE Symposium on Security and Privacy, 2018.
[13] Anthony D. Joseph, Blaine Nelson, Benjamin I. P. Rubinstein, and J. D. Tygar. Adversarial Machine
Learning. Cambridge University Press, 2018. in press.
[14] Kwang-Sung Jun, Lihong Li, Yuzhe Ma, and Xiaojin Zhu. Adversarial attacks on stochastic bandits.
In Advances in Neural Information Processing Systems (NIPS), 2018.
[15] L. Lessard, X. Zhang, and X. Zhu. An Optimal Control Approach to Sequential Machine Teaching.
ArXiv e-prints, October 2018.
[16] Bo Li and Yevgeniy Vorobeychik. Scalable Optimization of Randomized Operational Decisions in Ad-
versarialClassificationSettings. InGuyLebanonandS.V.N.Vishwanathan,editors,Proceedings ofthe
Eighteenth International Conference on Artificial Intelligence and Statistics, volume 38 of Proceedings
of Machine Learning Research, pages 599–607,San Diego, California, USA, 09–12 May 2015. PMLR.
[17] Daniel Liberzon. Calculus of variations and optimal control theory: A concise introduction. Princeton
University Press, 2011.
[18] Weiyang Liu, Bo Dai, Ahmad Humayun, Charlene Tay, Chen Yu, Linda B Smith, James M Rehg,
and Le Song. Iterative machine teaching. In International Conference on Machine Learning, pages
2149–2158,2017.
[19] WeiyangLiu,BoDai,XingguoLi,ZhenLiu,JamesM.Rehg,andLeSong. Towardsblack-boxiterative
machine teaching. In ICML, volume 80 of JMLR Workshop and Conference Proceedings, pages 3147–
3155.JMLR.org, 2018.
[20] DanielLowdandChristopherMeek. Adversariallearning. InProceedings oftheeleventhACMSIGKDD
international conference on Knowledge discovery in data mining, pages 641–647.ACM, 2005.
7

## Page 8

[21] ShikeMeiandXiaojinZhu. Usingmachineteachingtoidentifyoptimaltraining-setattacksonmachine
learners. In The Twenty-Ninth AAAI Conference on Artificial Intelligence, 2015.
[22] Kaustubh Patil, Xiaojin Zhu, Lukasz Kopec, and Bradley Love. Optimal teaching for limited-capacity
human learners. In Advances in Neural Information Processing Systems (NIPS), 2014.
[23] B.Recht. ATourofReinforcementLearning: TheViewfromContinuousControl. ArXive-prints,June
2018.
[24] AyonSen,PuravPatel,MartinaA.Rau,BlakeMason,RobertNowak,TimothyT.Rogers,andXiaojin
Zhu. Machine beats human at sequencing visuals for perceptual-fluency practice. In Educational Data
Mining, 2018.
[25] Emanuel Todorov. Optimal control theory. Bayesian brain: probabilistic approaches to neural coding,
pages 269–298,2006.
[26] Yevgeniy Vorobeychik and Murat Kantarcioglu. Adversarial machine learning. Synthesis Lectures on
Artificial Intelligence and Machine Learning, 12(3):1–169,2018.
[27] XiaojinZhu.Machineteaching: aninverseproblemtomachinelearningandanapproachtowardoptimal
education. In The Twenty-Ninth AAAI Conference on Artificial Intelligence (AAAI “Blue Sky” Senior
Member Presentation Track), 2015.
[28] XiaojinZhu,JiLiu, andManuelLopes. No learnerleft behind: Onthe complexity ofteaching multiple
learners simultaneously. In The 26th International Joint Conference on Artificial Intelligence (IJCAI),
2017.
[29] Xiaojin Zhu, Adish Singla, Sandra Zilles, and Anna N. Rafferty. An Overview of Machine Teaching.
ArXiv e-prints, January 2018. https://arxiv.org/abs/1801.05927.
8