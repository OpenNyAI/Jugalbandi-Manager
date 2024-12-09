# import pytest
# from unittest.mock import patch, MagicMock
# from lib.db_session_handler import DBSessionHandler
# from lib.data_models import Flow
# from lib.kafka_utils import KafkaProducer
# from app.extensions import produce_message
# import os

# # channel_input = Channel(
# #             source="api",
# #             turn_id=turn_id,
# #             intent=ChannelIntent.CHANNEL_IN,
# #             bot_input=RestBotInput(
# #                 channel_name=chosen_channel.get_channel_name(),
# #                 headers=headers,
# #                 data=message_data,
# #                 query_params=query_params,
# #             ),
# #         )
# @pytest.mark.asyncio
# @patch('api.app.extensions.KafkaProducer.from_env_vars')
# @patch.dict(os.environ, {'KAFKA_FLOW_TOPIC': 'flow', 'KAFKA_CHANNEL_TOPIC': 'channel', 'KAFKA_INDEXER_TOPIC': 'indexer'})
# async def test_produce_message_for_flow_instance(mock_kafka_producer):
    
#     flow_input = Flow(
#         source = "Api",
#         intent = "User input"
#     )
#     mock_producer = MagicMock()
#     mock_kafka_producer.return_value = mock_producer

#     flow_topic = "flow_topic"
    
#     produce_message(flow_input)

#     mock_producer.send_message.assert_called_once_with(
#         topic=flow_topic,
#         value=flow_input.model_dump_json(exclude_none=True)
#     )
