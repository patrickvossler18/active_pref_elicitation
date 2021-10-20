from elicitation_for_website.get_next_query import get_next_query
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SessionInfoSerializer, ChoicesSerializer, FormInfoSerializer
from .models import SessionInfo, Choices, FormInfo
from .policy_data import covid_data
from .choice_paths import choices_data
from elicitation_for_website.preference_classes import Item, Query
import random

ALGO_STAGE_MAP = {
    "adaptive": 0,
    "random": 1,
    "validation": 0
}

def get_last_stage(algo_stage_list):
    return algo_stage_list[-1]

# TO-DO: perhaps move this function to a util file?
def create_all_policies_list(json_data):
    all_policies = []
    for i in range(len(json_data)):
        all_policies.append(Item(json_data[i]['values'], i, json_data[i]['labels']))
    return all_policies

all_policies = create_all_policies_list(covid_data)

# The viewsets base class provides an implementation of CRUD operations by default
# But we only want to create new data, not anything else
# class SessionInfoView(viewsets.ModelViewSet):
#     serializer_class = SessionInfoSerializer
#     queryset = SessionInfo.objects.all()
class SessionInfoView(mixins.CreateModelMixin,
                  GenericAPIView):
    queryset = SessionInfo.objects.all()
    serializer_class = SessionInfoSerializer
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# Mixin that allows to create multiple objects from lists.
class CreateListModelMixin(object):
    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CreateListModelMixin, self).get_serializer(*args, **kwargs)

class ChoicesView(CreateListModelMixin, CreateAPIView):
    # Here we are expecting to get a JSON object with the session id,
    # an array of user choices
    # and an array of arrays of policies shown
    # queryset = Choices.objects.all()
    serializer_class = ChoicesSerializer


class FormInfoView(mixins.CreateModelMixin, GenericAPIView):
    queryset = FormInfo.objects.all()
    serializer_class = FormInfoSerializer
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

def get_smallest_gamma_stub():
    print("[WARN]: Using get_smallest_gamma_stub() function")
    return random.randint(1, 100) / 100.0

def elicitation_data_prep(json_data, response_data):
    """ transform the response data and json data to return a list of Query objects
    Args:
        json_data: the policy data set
        response_data: a dictionary with policiesShown as list of list of policies
        and userChoices as as list of the choices of the user
    """
    answered_queries = []
    user_choices = [int(val) for val in response_data.get('userChoices')]
    policies_shown = response_data.get('policiesShown')
    # TO-DO: safer way to loop through or maybe assert equal length of the lists
    for i in range(len(policies_shown)):
        # generate the items for each policy
        current_policy = policies_shown[i]
        current_choice = user_choices[i]
        policy_A = current_policy[0]
        policy_B = current_policy[1]
        # Item(features, id, feature_names)
        item_A = Item(json_data[policy_A]['values'], policy_A,
         json_data[policy_A]['labels'])
        item_B = Item(json_data[policy_B]['values'], policy_B,
         json_data[policy_B]['labels'])
        answered_queries.append(Query(item_A, item_B, current_choice))
    
    # looks like the current gamma just chooses a random integer?
    current_gamma = get_smallest_gamma_stub()
    return answered_queries, current_gamma


def choice_path_data_prep(response_data):
    """ transform the response data and json data to return a tuple of tuples to use as a look up key in the choices path dictionary
    Args:
        json_data: the policy data set
        response_data: a dictionary with policiesShown as list of list of policies
        and userChoices as as list of the choices of the user
    """
    answered_queries = ()
    user_choices = [int(val) for val in response_data.get('userChoices')]
    policies_shown = response_data.get('policiesShown')
    # TO-DO: safer way to loop through or maybe assert equal length of the lists
    for i in range(len(policies_shown)):
        # generate the items for each policy
        current_policy = policies_shown[i]
        current_choice = user_choices[i]
        policy_A = current_policy[0]
        policy_B = current_policy[1]
        answered_queries.append((policy_A, policy_B, current_choice))
    return answered_queries

def look_up_choice(answered_queries,  choices_data):
    next_query_tuple = choices_data.get(answered_queries, None)
    item_A, item_B = next_query_tuple[1]
    predicted_response = next_query_tuple[2]
    recommended_item = next_query_tuple[0]
    return item_A, item_B, predicted_response, recommended_item
# NextChoice is a generic view
class NextChoiceView(APIView):
    # TO-DO: do checks on request data 
    # dynamic way to choose which data set?
    # maybe add dataset name to request?
    # TO-DO: Do we need to track gamma?
    # TO-DO: add logic for once we are in the validation stage
    def post(self, request, format=None):
        print(dict(request.data))
        print(request.data)
        current_stage = get_last_stage(request.data['prevStages'])
        f_random = ALGO_STAGE_MAP[current_stage]
        recommended_item = None
        # need to handle different logic for if random or adaptive here. usually this is done in get next_query
        if f_random == 1:
            answered_queries, current_gamma = elicitation_data_prep(covid_data, request.data)
            item_A, item_B, predicted_response, objval = get_next_query(all_policies, answered_queries,f_random=f_random, verbose=True)
        else:
            # what if we are in the validation stage?
            answered_queries = choice_path_data_prep(request.data)
            item_A, item_B, predicted_response, recommended_item = look_up_choice(answered_queries, choices_data)
        print(f"item A: {item_A}, item B: {item_B}, prediction: {predicted_response}, recommended_item: {recommended_item}")
        # we need to store the recommended item information on the front end
        response_dict = {"policy_ids": [item_A, item_B], "prediction" : predicted_response, "recommended_item": recommended_item}
        return Response(response_dict)

class PolicyDataView(APIView):
    def get(self, request, format=None):
        dataset_name = request.GET.get('dataset',None)
        if dataset_name is not None:
            if dataset_name == "COVID":
                return Response({'data': covid_data})
            if dataset_name == "LAHSA":
                return Response({'data': lahsa_data})
            else:
                return Response(None)
        else:
            return Response(None)
