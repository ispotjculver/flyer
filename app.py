import random
import uuid
from uuid import uuid4
import concurrent.futures

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

from flask import Flask, request, jsonify
import boto3
import json
import requests
from config import Config
from typing import Dict, Any, Optional

app = Flask(__name__)

# ace_live_demo_uuids = [gender, age, income, ethnicity, kids, zip]
ace_live_demo_uuids = ["be3e7c45-1089-410a-96c0-c90aa06702af", "2fa7e679-3923-4305-b35d-5f31d85992b9", "5b537309-eaab-4544-8fce-899f2130bd7d", "601dae29-e6d8-4479-93e2-ad22b97dcae0", "82538095-4009-4196-befb-f9c34403127e", "e12f3ab7-b61e-4d63-8a2f-4475c9ce92db"]
ethnicity_probs = [.5, .15, .15, .1, .1]


class SurveyTaker:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.proxies = {
            'http': 'http://stage-proxyvip.acemetrix.com:3128/',
            'https': 'http://stage-proxyvip.acemetrix.com:3128/'
        }
        with open('wordbank.txt', 'r') as f:
            self.word_bank = [word.strip() for word in f.readlines()]
        with open('zipcodes.txt', 'r') as f:
            self.zip_codes = [zip_code.strip() for zip_code in f.readlines()]

    def create_participant(self, survey_token: str, provider_code: str, participant_key: str, secret_key: str) -> str:
        ua = 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36'
        random_id = uuid.uuid4()
        create_url = f"{Config.SURVEY_API_BASE_URL}/api/participations/?orientation=true&touch=true&p={provider_code}&t={survey_token}&{participant_key}={random_id}"
        if secret_key is not None and len(secret_key) > 0:
            cipher = AES.new(secret_key.encode()[:32].ljust(32, b'\0'), AES.MODE_ECB)
            encrypted_key = base64.b64encode(cipher.encrypt(pad(str(random_id).encode(), AES.block_size))).decode()
            create_url += f"&v{participant_key}={encrypted_key}"
        response = requests.post(
            create_url,
            headers={"User-Agent": ua},
            proxies=self.proxies
        )
        response.raise_for_status()
        return response.json()

    def progress_participant(self, participation_id: str, payload: Dict[str, Any]) -> str:
        ua = 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36'
        response = requests.post(
            f"{Config.SURVEY_API_BASE_URL}/api/participations/{participation_id}/next",
            headers={"User-Agent": ua},
            json=payload,
            proxies=self.proxies
        )
        response.raise_for_status()
        return response.json()

    def get_flight_data(self, survey_uuid: str) -> tuple:
        response = requests.get(
            f"{Config.SURVEY_API_BASE_URL}/api/flights/{survey_uuid}",
            proxies=self.proxies
        )
        response.raise_for_status()
        flight_data = response.json()

        response = requests.get(
            f"{Config.SURVEY_API_BASE_URL}/api/providers/{flight_data['provider']['id']}",
            proxies=self.proxies
        )
        response.raise_for_status()
        provider_data = response.json()

        return flight_data["token"], provider_data["code"], provider_data["participantKeyParam"], provider_data["secretKey"]

    def update_flight_surveytaker(self, survey_uuid: str, survey_taker: str):
        response = requests.put(
            f"{Config.SURVEY_API_BASE_URL}/api/flights/{survey_uuid}/?status=open&surveytaker={survey_taker}",
            proxies=self.proxies
       )
        response.raise_for_status()
        return response.json()


    def format_response(self, participation_id: str, step_id: int, responses: list) -> Dict[str, Any]:
        sample_response = {"bandwidth": 22260.939130434785, "bandwidthCheckCanceled": True, "ping": {
            "pingMean": 101,
            "pingVariance": 1,
            "numberOfFailedPings": 0
        }, "stepId": step_id, "participantId": participation_id, "responses": responses}
        return sample_response

    def get_fake_scores(self, length: int) -> list:
        scores = [ {
                "time": 0,
                "value": 50,
                "timeStamp": 1764020657595,
                "direction": 100,
                "scoreBefore": 50
            },
            {
                "time": 0.221979,
                "value": 50,
                "timeStamp": 1764020657840,
                "scoreBefore": 50
            },
            {
                "time": length - .2,
                "value": 50,
                "timeStamp": 1764020672547,
                "direction": -110,
                "scoreBefore": 50
            },
            {
                "time": length - .2,
                "value": 50,
                "timeStamp": 1764020672553,
                "direction": -100,
                "scoreBefore": 50
            }]
        return scores

    def get_substep_responses(self, substeps: list, question_ids: list, demo_answers: Dict[str, Any]) -> list:
        responses = []
        for s in substeps:
            sid = s.get("id")
            stype = s.get("type")

            if sid not in question_ids:
                continue

            match stype:
                case "radio":
                    if sid in demo_answers:
                        responses.append({"id": sid, "value": demo_answers[sid]})
                        continue
                    if sid == "601dae29-e6d8-4479-93e2-ad22b97dcae0":
                        random_choice = random.choices(s["choices"], weights=ethnicity_probs)[0]
                    else:
                        random_choice = s["choices"][random.randint(0, len(s["choices"]) - 1)]
                    radio_response = {"id": sid, "value": random_choice["id"]}
                    if "flag" in random_choice and random_choice["flag"] == "BRAND":
                        radio_response["inputText"] = random.sample(self.word_bank, 1)[0]
                    responses.append(radio_response)
                    ## HANDLE BRAND
                case "number":
                    if "range" in s:
                        if sid in demo_answers:
                            responses.append({"id": sid, "value": str(2025 - int(demo_answers[sid]))})
                            continue
                        age_groups = [(1945, 1975), (1976, 1989), (1990, 2004), (2005, 2007)]
                        age_weights = [0.31, 0.31, 0.31, 0.07]
                        selected_range = random.choices(age_groups, weights=age_weights)[0]
                        random_range = random.randint(selected_range[0], selected_range[1])
                        responses.append({"id": sid, "value": str(random_range)})
                    else:
                        random_zip = random.choice(self.zip_codes)
                        responses.append({"id": sid, "value": str(random_zip)})
                case "instructions_video":
                    pass
                case "diagnostic":
                    responses.append({"id": sid, "scores": self.get_fake_scores(s["length"])})
                case "imagegrid":
                    random_choice = s["choices"][random.randint(0, len(s["choices"]) - 1)]["id"]
                    responses.append({"id": sid, "value": random_choice})
                case "slider":
                    random_range = random.randint(1, 99)
                    responses.append({"id": sid, "value": random_range})
                case "textarea":
                    random_words = random.sample(self.word_bank, 3)
                    responses.append({"id": sid, "value": " ".join(random_words)})
                case "checkbox":
                    random_choice = s["choices"][random.randint(0, len(s["choices"]) - 1)]["id"]
                    responses.append({"id": sid, "value": [random_choice]})
        return responses
    
    def take_survey(self, survey_token: str, provider_code: str, participant_key: str, secret_key: str, demo_answers: Dict[str, Any]) -> bool:
        survey_fin = False
        survey_complete = False
        current_ppt = self.create_participant(survey_token, provider_code, participant_key, secret_key)
        ppt_id = current_ppt.get("participationId")

        while not survey_fin:
            step_id = current_ppt.get("stepId")
            if step_id == -1:
                print(f"REJECTED: {current_ppt}")
                survey_fin = True
                if current_ppt.get("substeps")[0]["errorCode"] in [301,302]:
                    survey_complete = True
                continue
            if current_ppt.get("meta").get("finished"):
                survey_fin = True
                continue
            responses = self.get_substep_responses(current_ppt.get("substeps"), current_ppt.get("meta").get("questionIds"), demo_answers)
            current_ppt = self.progress_participant(ppt_id, self.format_response(ppt_id, step_id, responses))
        
        return survey_complete

    def get_replay_data(self, replay_uuid: str) -> list:
        try:
            bucket = 'amx-sv2-raw-prod'
            prefix = f"flights/{replay_uuid}/participations/"
            
            participation_data = []
            continuation_token = None
            
            while True:
                kwargs = {'Bucket': bucket, 'Prefix': prefix}
                if continuation_token:
                    kwargs['ContinuationToken'] = continuation_token
                
                response = self.s3_client.list_objects_v2(**kwargs)
                
                for obj in response.get('Contents', []):
                    file_response = self.s3_client.get_object(
                        Bucket=bucket,
                        Key=obj['Key']
                    )
                    participation_data.append(json.loads(file_response['Body'].read()))
                    break
                
                if not response.get('IsTruncated'):
                    break
                continuation_token = response.get('NextContinuationToken')

            filtered_ppt = list(filter(lambda x: len(x.get('responseSets')) > 0 and len(x.get('responseSets')[0].get('responses')) == 6 and type(x.get('lastActivity')) == int, participation_data))
            filtered_ppt.sort(key=lambda x: int(x.get('lastActivity')))

            return filtered_ppt
        except Exception as e:
            raise Exception(f"Failed to fetch replay data: {str(e)}")
    
    def get_demo_answers(self):
        with open('demo_answers.json', 'r') as f:
            return json.load(f)

survey_taker = SurveyTaker()

@app.route('/survey/take', methods=['POST'])
def take_survey():
    survey_uuid = request.json.get('survey_uuid')
    
    if not survey_uuid:
        return jsonify({"error": "survey_uuid parameter required"}), 400

    survey_token, provider_code, participant_key, secret_key = survey_taker.get_flight_data(survey_uuid)
    
    try:
        survey_taker.update_flight_surveytaker(survey_uuid, "true")
        
        total_completed = 0
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(survey_taker.take_survey, survey_token, provider_code, participant_key, secret_key, {}) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            total_completed += len(results)
            if any(results):
                break
        
        survey_taker.update_flight_surveytaker(survey_uuid, "false")
        return jsonify({"completed": total_completed, "successful": sum(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/survey/replay', methods=['POST'])
def replay_survey():
    survey_uuid = request.json.get('survey_uuid')
    replay_uuid = request.json.get('replay_uuid')
    repeat = request.json.get('repeat')
    
    if not survey_uuid:
        return jsonify({"error": "survey_uuid parameter required"}), 400

    survey_token, provider_code, participant_key, secret_key = survey_taker.get_flight_data(survey_uuid)
    
    try:
        if replay_uuid:
            replay_data = survey_taker.get_replay_data(replay_uuid)
            print(f"Replaying {len(replay_data)} participants from flight {replay_uuid}")
        else:
            print("Using demo answers for replay")
        
        survey_taker.update_flight_surveytaker(survey_uuid, "true")
        survey_closed = False

        def loop_replay():
            survey_complete = False
            if replay_uuid:
                demo_answers = {}
                for ppt in replay_data:
                    for r in ppt.get('responseSets')[0].get('responses'):
                        if r.get('questionUuid') in ace_live_demo_uuids:
                            if r.get('age') is not None:
                                demo_answers[r.get('questionUuid')] = r.get('age')
                                continue
                            if r.get('text') is not None:
                                demo_answers[r.get('questionUuid')] = r.get('text')
                                continue
                            demo_answers[r.get('questionUuid')] = r.get('choices')[0]['uuid']
                    survey_complete = survey_taker.take_survey(survey_token, provider_code, participant_key, secret_key, demo_answers)
                    if survey_complete:
                        break
            else:
                demo_answers = survey_taker.get_demo_answers()
                for d in demo_answers:
                    survey_complete = survey_taker.take_survey(survey_token, provider_code, participant_key, secret_key, d)
                    if survey_complete:
                        break
            return survey_complete

        if repeat:
            while not survey_closed:
                survey_closed = loop_replay()
        else:
            loop_replay()

        survey_taker.update_flight_surveytaker(survey_uuid, "false")
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)