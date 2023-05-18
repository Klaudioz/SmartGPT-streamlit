import openai
import streamlit as st


class SmartGPTAgent:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        if not self.api_key:
            st.error("API Key is not set.")
            st.stop()

    def generate_response(self, dialogues):
        result = openai.ChatCompletion.create(
            model=self.model,
            messages=dialogues,
            max_tokens=2000,
            n=1,
            stop=None,
            temperature=0.5,
        )

        return result.choices[0].message['content'].strip()

    def generate_answers(self, question, number_of_answers):
        dialogues = [{"role": "user", "content": question}]
        answers = []

        for i in range(number_of_answers):
            answer = self.generate_response(dialogues)
            answers.append(f"Answer Option {i + 1}: {answer}")
            dialogues.append({"role": "assistant", "content": answer})

        return answers

    def execute(self, question, number_of_answers):
      answers = self.generate_answers(question, number_of_answers)
      answers_text = '\n'.join(answers)
      researcher_prompt = f"""
      {question}

      {answers_text}

      You are a researcher tasked with investigating the {number_of_answers} answer options provided.
      List the flaws and faulty logic of each answer option. Let's think step by step.
      """

      researcher_response = self.generate_response([
          {"role": "user", "content": question},
          {"role": "assistant", "content": "\n".join(answers)},
          {"role": "user", "content": researcher_prompt},
      ])

      resolver_prompt = f"""
      You are a resolver tasked with:
      - Finding which of the {number_of_answers} answer options the researcher thought was best
      - Improving that answer
      - Printing out the improved answer in full.
      Let's work this out in a step by step way to be sure we have the right answer: 
      """

      resolver_response = self.generate_response([
          {"role": "user", "content": question},
          {"role": "assistant", "content": "\n".join(answers)},
          {"role": "user", "content": researcher_prompt},
          {"role": "assistant", "content": researcher_response},
          {"role": "user", "content": resolver_prompt},
      ])

      return resolver_response


def main():
    st.title('SmartGPT')

    api_key = st.text_input("API Key", type="password")
    model = st.selectbox('Select Model', ['gpt-3.5-turbo', 'gpt-4'])
    question = st.text_input('Ask a question:')
    number_of_answers = st.number_input('Select number of answers', min_value=3, value=3, step=1)

    answer_placeholder = st.empty()

    if st.button('Submit'):
        agent = SmartGPTAgent(api_key, model)
        with st.spinner('Generating response...'):
            answer = agent.execute(question, number_of_answers)
        answer_placeholder.text_area("Answer", answer, height=600)

if __name__ == '__main__':
    main()
