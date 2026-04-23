INFOSEEK_FEW_SHOTS = (
    {
        'context': [
            "The myrtle warbler (Setophaga coronata) is a small New World warbler.The myrtle warbler has a northerly and easterly distribution, with Audubon\'s further west.",
            "The summer male myrtle warbler has a slate blue back, and yellow crown, rump and flank patch. It has white tail patches, and the breast is streaked black.",
            "The stem is greyish green, usually 7-20 (cm) (in Southern Europe exceptionally 40\xa0cm) high, unbranched, erect, and terete. Especially further up, the stem is covered with short transparent glandular hairs."
        ],
        'question': "What is the closest parent taxonomy of this bird?",
        'answer': "Myrtle Warbler"
    },
    {
        'context': [
            "When threatened, however, they can reach up to 40 (km/h) and maintain that speed for 150 (m). Wombats defend home territories centred on their burrows, and they react aggressively to intruders. The common wombat occupies a range of up to 23 (ha), while the hairy-nosed species have much smaller ranges, of no more than 4 (ha).",
            "Female wombats give birth to a single young after a gestation period of roughly 20–30 days, which varies between species. All species have well-developed pouches, which the young leave after about six to seven months. Wombats are weaned after 15 months, and are sexually mature at 18 months",
            "For instance, the American Ornithologists' Union places larks just after the crows, shrikes, and vireos. At a finer level of detail, some now place the larks at the beginning of a superfamily Sylvioidea with the swallows, various \"Old World warbler\" and \"babbler\" groups, and others."
        ],
        'question': "How many offspring can this animal produce at the same time?",
        'answer': "1.0"
    },
    {
        'context': [
            "In the summer of 2005, original owner Madeleine Paulson provided the Old Friends Equine retirement facility in Georgetown, Kentucky with a substantial gift to enable them to acquire the horse, bring him home from Japan, and look after him during his retirement years.On November 7, 2005, the seventeen-year-old Fraise died suddenly from a ruptured blood vessel in his abdomen.",
            "Fraise (1988–2005) was an American Thoroughbred racehorse best known for winning the 1992 Breeders' Cup Turf.## Background.Fraise was a bay horse bred by Allen E. Paulson.",
            "These are sometimes referred to as chip art, silicon art, silicon graffiti or silicon doodling. The 555 timer IC The Operational amplifier 7400-series integrated circuits 4000-series integrated circuits, the CMOS counterpart to the 7400 series (see also: 74HC00 series)"
        ],
        "question": "In which year was this animal born?",
        'answer': "1988"
    }
)

INFOSEEK_FEW_SHOTS = """
Here are three good examples of the format that you MUST follow when answering the question based on the image and context.

Example 1:
What is the closest parent taxonomy of this bird?

The following paragraphs may contain useful information to help answer the question correctly:

The myrtle warbler (Setophaga coronata) is a small New World warbler.The myrtle warbler has a northerly and easterly distribution, with Audubon's further west.
The summer male myrtle warbler has a slate blue back, and yellow crown, rump and flank patch. It has white tail patches, and the breast is streaked black.
The stem is greyish green, usually 7-20 (cm) (in Southern Europe exceptionally 40 cm) high, unbranched, erect, and terete. Especially further up, the stem is covered with short transparent glandular hairs.

Answer:
<think> The image shows a small bird with a distinctive yellow crown, rump, and flank patch, along with a slate blue back and white tail patches. These features are characteristic of the myrtle warbler. The retrieved passages provide information about the myrtle warbler, including its scientific name (Setophaga coronata) and its physical description, which matches the bird in the image. The question asks for the closest parent taxonomy of this bird. The passage explicitly identifies the bird as a myrtle warbler, which is the answer to the question. Therefore, the passage is relevant and provides the necessary information to answer the question.</think>
<answer>Myrtle Warbler</answer>

Example 2:
How many offspring can this animal produce at the same time?

The following paragraphs may contain useful information to help answer the question correctly:

When threatened, however, they can reach up to 40 (km/h) and maintain that speed for 150 (m). Wombats defend home territories centred on their burrows, and they react aggressively to intruders. The common wombat occupies a range of up to 23 (ha), while the hairy-nosed species have much smaller ranges, of no more than 4 (ha).
Female wombats give birth to a single young after a gestation period of roughly 20–30 days, which varies between species. All species have well-developed pouches, which the young leave after about six to seven months. Wombats are weaned after 15 months, and are sexually mature at 18 months
For instance, the American Ornithologists' Union places larks just after the crows, shrikes, and vireos. At a finer level of detail, some now place the larks at the beginning of a superfamily Sylvioidea with the swallows, various "Old World war bler" and "babbler" groups, and others.

Answer:
<think> The image shows a wombat, a marsupial known for its burrowing behavior. The question asks how many offspring this animal can produce at the same time. The retrieved passage provides relevant information about wombat reproduction, specifically stating that "Female wombats give birth to a single young after a gestation period of roughly 20–30 days." This directly answers the question, indicating that wombats produce one offspring at a time. Therefore, the passage is relevant and provides the necessary information to answer the question.</think>
<answer>1.0</answer>

Example 3:
In which year was this animal born?

The following paragraphs may contain useful information to help answer the question correctly:

In the summer of 2005, original owner Madeleine Paulson provided the Old Friends Equine retirement facility in Georgetown, Kentucky with a substantial gift to enable them to acquire the horse, bring him home from Japan, and look after him during his retirement years.On November 7, 2005, the seventeen-year-old Fraise died suddenly from a ruptured blood vessel in his abdomen.
Fraise (1988–2005) was an American Thoroughbred racehorse best known for winning the 1992 Breeders' Cup Turf.## Background.Fraise was a bay horse bred by Allen E. Paulson.
These are sometimes referred to as chip art, silicon art, silicon graffiti or silicon doodling. The 555 timer IC The Operational amplifier 7400-series integrated circuits 4000-series integrated circuits, the CMOS counterpart to the 7400 series (see also:74HC00 series)

Answer:
<think> The image shows a racehorse, and the question asks for the year in which this animal was born. The retrieved passage provides relevant information about a specific racehorse named Fraise, stating that "Fraise (1988–2005) was an American Thoroughbred racehorse." This indicates that Fraise was born in 1988. Since the image depicts a racehorse and the passage provides the birth year of a racehorse, it is reasonable to conclude that the passage is relevant and provides the necessary information to answer the question.</think>
<answer>1988</answer>
"""

EVQA_FEW_SHOTS = """
Here are two good examples of the format that you MUST follow when answering the question based on the image and context.


Example 1:
On what side of this park does i-78 run?
The following paragraphs may contain useful information to help answer the question correctly:
In 2000, andrea bocelli gave a concert at the park, broadcast on pbs, as american dream: andrea bocelli's statue of liberty concert.\nin 2001, cirque du soleil premiered its new work.\nin 2013, cher, tim mcgraw, miguel, mariah carey and selena gomez performed at the park for the macy's fourth of july fireworks spectacular.\nthe super bowl li kickoff spectacular was held by the communipaw terminal in 2014, and featured performances from goo goo dolls, and daughtry. erin andrews, jordin sparks, and joe buck hosted the event.\njersey city's freedom and fireworks festival debuted in the park in 2017 independence day and included performances from fireworks by grucci and the jersey city-based kool & the gang. the festival has since been held in the city's exchange place neighborhood.\nalicia keys and swae lee performed at the park for the 2021 mtv video music awards

Answer: <think> The image shows a waterfront park with a view of a city skyline across a body of water. There are benches along a paved path, suggesting a pedestrian area designed for public use. The passage mentions various concerts and events held at a park, but it does not specify the location of the park relative to any major roads or highways. The question asks about the side of the park where I-78 runs, which is not addressed in the passage. The passage is irrelevant because it does not provide any information about the location of the park or the highway. The image, while showing a waterfront park, does not give enough context to determine the specific location of the park or the presence of I-78. Therefore, the passage cannot be used to deduce the answer to the question.</think>
<answer> western </answer>


Example 2:
What soil type does this tree grow in?

The following paragraphs may contain useful information to help answer the question correctly:
in the north, mockernut hickory is found on drier soils of ridges and hillsides and less frequently on moist woodlands and alluvial bottoms. the species grows and develops best on deep, fertile soils. in the cumberland mountains and hills of southern indiana, it grows on dry sites such as south and west slopes or dry ridges. in alabama and mississippi, it grows on sandy soils with shortleaf pine (pinus echinata) and loblolly pine (p taeda). however, most of the merchantable mockernut grows on moderately fertile upland soils.\nmockernut hickory grows primarily on ultisols occurring on an estimated 65% of its range, including much of the southern to northeastern united states. these soils are low in nutrients and usually moist, but during the warm season, they are dry part of the time. along the mid-atlantic and in the southern and western range, mockernut hickory grows on a variety of soils on slopes of 25% or less, including combinations of fine to coarse loams, clays, and well-drained quartz sands. on slopes steeper than 25%, mockernut often grows on coarse loams.\nmockernut grows on inceptisols in an estimated 15% of its range. these clayey soils are moderate to high in nutrients and are primarily in the appalachians on gentle to moderate slopes, where water is available to plants during the growing season. in the northern appalachians on slopes of 25% or less, mockernut hickory grows on poorly drained loams with a fragipan. in the central and southern appalachians on slopes 25% or less, mockernut hickory grows on fine loams. on steeper slopes, it grows on coarse loams.\nin the northwestern part of the range, mockernut grows on mollisols. these soils have a deep, fertile surface horizon greater than 25cm (9.8in) thick. mollisols characteristically form under grass in climates with moderate to high seasonal precipitation.\nmockernut grows on a variety of soils including wet, fine loams, sandy textured soils that often have been burned, plowed, and pastured. alfisols are also present in these areas and contain a medium to high supply of nutrients. water is available to plants more than half the year or more than three consecutive months during the growing season. on slopes of 25% or less, mockernut grows on wet to moist, fine loam soils with a high carbonate content.

Answer:
<think> The image shows a mockernut hickory tree. The retrieved passage discusses various soil types suitable for this tree, explicitly mentioning "coarse loams", "quartz sands", "clays", and "fine loams". The text is highly relevant and lists the specific soil types associated with this species.</think>
<answer>coarse loams and quartz sands and clays and fine loams and sandy textured soils</answer>
"""

VQA_PROMPT = (
"Answer the question based on the image above.\n\n"
"Question: {question}\n\n"
)

CONTEXT_VQA_PROMPT_training="""\
{question}

The following paragraphs may contain useful information to help answer the question correctly:
{context}
"""

RELEVANCY_EVAL_SYSTEM_PROMPT = """\
You are a multimodal reasoning assistant specialized in Knowledge-Based Visual Question Answering (KB-VQA).
Your task is to evaluate whether a given text passage provides useful and relevant information for answering a question about an image.

You will be given:
- Image: a visual scene containing entities, actions, and context.
- Question: a natural-language question that refers to the image.
- Text Passage: an external knowledge snippet retrieved from a database or the web.

You must analyze the semantic alignment between the text, the image, and the question.
Follow these steps carefully before giving your final decision:
1. Understand the visual scene: Identify the key objects, people, actions, and context visible in the image.
2. Interpret the question: Determine what information the question seeks (e.g., factual, reasoning, counting, attribute-based).
3. Analyze the text passage: Extract the main claims, facts, and entities mentioned in the text.

Compare for relevance: Assess whether the information in the text:
- Contains at least one sentence that supports answering the question about the image, OR
- Provides background knowledge needed to interpret or reason about the image-question pair.

Important:
- If even a single sentence in the passage is relevant or useful, consider the entire passage as **relevant** and answer “Yes”.
- If no part of the passage contributes meaningfully to answering the question, answer “No”.

Output only one word:
"Yes" -> if the text provides relevant or useful information for answering the question.
"No" -> if the text is irrelevant or unhelpful.\
"""


SECTION_EVAL_USER_TEMPLATE = """\
Here is the question on the image above: 
{question}

Here is the text passage to analyze:
{passage}

Does the text passage contain at least one sentence that may have some information usefule to answer the user question? 
"Yes"/"No" answer: \
"""


SYSTEM_PROMPT_REASONING = "A conversation between User and Assistant. The user asks a question, and the Assistant solves it. The assistant first thinks about the reasoning process in the mind and then provides the user with the answer. The reasoning process and answer are enclosed within <think> </think> and <answer> </answer> tags, respectively, i.e., <think>reasoning process here</think><answer>short answer here</answer>"


REASONING_TRACE_EXTRACTION_SYSTEM_PROMPT = """\
You are a multimodal reasoning assistant.
Your goal is to analyze the image and the question, and then produce a hidden reasoning trace that logically leads to the given answer.
The reasoning must be step-by-step, plausible, and based on the visual evidence and the question.
Do not mention, restate, or hint at the correct answer provided to you in the reasoning trace.
Output your reasoning and the correct answer using the exact format below:

```
<think> [your reasoning trace here] </think>
<answer> [the provided answer] </answer>
```\
"""

REASONING_TRACE_EXTRACTION_USER_TEMPLATE = """\
Question: {question}
Correct Answer: {answer}

Please produce a reasoning trace that could lead to this answer, but without mentioning or hinting at it explicitly.
Focus on describing visual evidence, spatial relations, object properties, and logical deductions based on what is visible.\
"""

EXAMPLE_1="""
EXAMPLE 1 with Relevant passage:

Question: What are the precocial young of this bird vulnerable to?

Retrieved relevant Passage: 
parental care is variable within birds and the kentish plover has a slightly different mechanism to other shorebirds. as discussed above, both parents incubate the eggs, however both parents do not always stick around once the eggs have hatched. it is not unusual for one parent to leave the chicks after a variable amount of time; this is referred to as brood desertion. brood desertion is the \u2018termination of care, by either one or both parents, before the offspring are capable of surviving independently\u2019 and usually occurs after one week of the brood being accompanied by both parents. brood desertion has been observed in both males and females, however females desert the brood significantly more frequently than males. \nstudies have shown that both the male and female kentish plover can provide adequate care for their brood on their own, so it is not the differences in the ability of the parents that determines which parent deserts the brood and which stays to care for the chicks. however, studies have also shown that after desertion females have a larger chance of breeding success than males, potentially due to many kentish plover populations maintaining a male-biased osr (operational sex ratio - the ratio of males actively breeding to females). therefore, is it hypothesized that the amount of reproductive success gained by desertion is what actually determines who deserts the brood,. in short, males and females can care for their brood equally, however females gain more by deserting their brood than males, resulting in a higher amount of female desertion over male. the non-deserting parent can continue to brood their chicks up to 80% of the time for over 20 days after hatching, as precocial young are vulnerable and exposed to external temperatures.\nif the parent bird feels that the eggs or chicks are under attack, then it will feign injury in order to divert attention towards itself.

Correct answer: "external temperatures"


Output:
<think> The image depicts a small shorebird with sandy-colored plumage, a black neck band, and a white underside which is characteristics of the Kentish plover. The question asks what the precocial young of this bird are vulnerable to. The retrieved passage provides detailed behavioral and ecological information about the Kentish plover. It explains that after hatching, one parent often deserts the brood, but the remaining parent can continue to provide care. The key point is that “the non-deserting parent can continue to brood their chicks up to 80% of the time for over 20 days after hatching, as precocial young are vulnerable and exposed to external temperatures.” This statement explicitly identifies that the chicks are vulnerable to external temperatures, implying that exposure to heat or cold could threaten their survival. The passage does not mention other dangers such as predators, so the relevant vulnerability is temperature-related. Thus, the text is directly relevant and provides the answer. </think>
<answer> external temperatures </answer>\
"""


EXAMPLE_2="""
EXAMPLE 2 with Irrelevant passage:

Question: What are the precocial young of this bird vulnerable to?

Retrieved irrelevant Passage: 
parental care is variable within birds and the kentish plover has a slightly different mechanism to other shorebirds. as discussed above, both parents incubate the eggs, however both parents do not always stick around once the eggs have hatched. it is not unusual for one parent to leave the chicks after a variable amount of time; this is referred to as brood desertion. brood desertion is the \u2018termination of care, by either one or both parents, before the offspring are capable of surviving independently\u2019 and usually occurs after one week of the brood being accompanied by both parents. brood desertion has been observed in both males and females, however females desert the brood significantly more frequently than males. \nstudies have shown that both the male and female kentish plover can provide adequate care for their brood on their own, so it is not the differences in the ability of the parents that determines which parent deserts the brood and which stays to care for the chicks. however, studies have also shown that after desertion females have a larger chance of breeding success than males, potentially due to many kentish plover populations maintaining a male-biased osr (operational sex ratio - the ratio of males actively breeding to females). therefore, is it hypothesized that the amount of reproductive success gained by desertion is what actually determines who deserts the brood,. in short, males and females can care for their brood equally, however females gain more by deserting their brood than males, resulting in a higher amount of female desertion over male. the non-deserting parent can continue to brood their chicks up to 80% of the time for over 20 days after hatching, as precocial young are vulnerable and exposed to external temperatures.\nif the parent bird feels that the eggs or chicks are under attack, then it will feign injury in order to divert attention towards itself.

Correct answer: "external temperatures"


Output:
<think> The image shows a bird with its young that are mobile and covered in down feathers, indicating that they are precocial—able to leave the nest shortly after hatching and feed themselves. The visual evidence highlights that the chicks are exposed on the ground or in an open environment, without full feather coverage or protection from the elements. This suggests that their survival may be influenced by environmental factors. <br>
The retrieved passage describes the spotless starling and its distribution but contains no information about the development, vulnerability, or environmental risks faced by its young. Therefore, the passage is largely irrelevant to answering the question.
From the visual evidence, the precocial chicks' exposure and incomplete feathering make them susceptible to environmental influences, particularly those related to the surrounding climate. Logical deduction from the image indicates that such young birds are at risk from changes in external conditions due to their limited physiological defenses and lack of shelter. </think>
<answer> external temperatures </answer>\
"""

REASONING_TRACE_EXTRACTION_SYSTEM_PROMPT_w_PASSAGE = """\
You are a multimodal reasoning assistant.
Your goal is to analyze the image, the question, and the retrieved passage, and then produce a hidden reasoning trace that logically leads to the given answer.
The reasoning must be step-by-step, plausible, and based on both the visual evidence and the retrieved text passage.
You MUST explicitly state, within your reasoning trace, whether the passage is relevant or not according to the information provided (i.e., if it is labeled as "irrelevant", your reasoning must clearly and logically explain why it is not relevant, and if it is labeled as "relevant", your reasoning must logically support its relevance).
Do not mention, restate, or hint at the correct answer in the reasoning trace.

Your reasoning trace should include:
- Description of relevant visual evidence (objects, spatial relations, attributes).
- Analysis of the retrieved passage (what it states, whether it supports or contradicts the image/question, and its relevance).
- Logical deduction that connects the visual and textual evidence to reach a conclusion.

Here you have two good examples of reasoning traces:
"""+EXAMPLE_1+EXAMPLE_2+"""


Output your reasoning and the correct answer using the exact format below:
```
<think> [your reasoning trace here] </think>
<answer> [the provided answer] </answer>
```\
"""

REASONING_TRACE_EXTRACTION_USER_TEMPLATE_w_PASSAGE = """\
Question: {question}
Retrieved {relevant} Passage: {passage}
Correct Answer: {answer}

Please produce a reasoning trace that could logically lead to this answer, based on both the image and the retrieved passage if relevant. 
Do not mention or hint at the answer explicitly in your reasoning.
Concentrate on providing a coherent explanation that supports the indicated relevance or irrelevance of the passage in the reasoning trace, integrating both textual and visual evidence.
Make sure to insert the correct answer between the answer tags.
"""


