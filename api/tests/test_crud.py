import pytest
from unittest import mock
from uuid import uuid4
from lib.db_session_handler import DBSessionHandler
from lib.models import JBUser, JBTurn, JBChannel, JBBot
from app.crud import (
    create_user, 
    create_turn, 
    get_user_by_number, 
    get_channel_by_id, 
    get_bot_list, 
    get_channels_by_identifier, 
    update_bot,
    update_channel,
    update_channel_by_bot_id,
)

class AsyncContextManagerMock:
    def __init__(self, session_mock):
        self.session_mock = session_mock

    async def __aenter__(self): 
        return self.session_mock
    
    async def __aexit__(self, exc_type, exc_val, exc_tb): 
        pass

class AsyncBeginMock:
    async def __aenter__(self):
        pass  
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  

@pytest.mark.asyncio
async def test_create_user_success():
    channel_id = "channel123"
    phone_number = "1234567890"
    first_name = "John"
    last_name = "Doe"

    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        user = await create_user(channel_id, phone_number, first_name, last_name)
        
        assert user is not None
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.identifier == phone_number
        assert user.channel_id == channel_id
        assert isinstance(user.id, str)  
        assert len(user.id) == 36  

        mock_session.commit.assert_awaited_once()
            
@pytest.mark.asyncio
async def test_create_user_db_failure():
    channel_id = "channel123"
    phone_number = "1234567890"
    first_name = "John"
    last_name = "Doe"

    with mock.patch.object(DBSessionHandler, 'get_async_session', side_effect=Exception("Database error")):
        with pytest.raises(Exception):
            await create_user(channel_id, phone_number, first_name, last_name)

@pytest.mark.asyncio
async def test_create_turn_success():
    bot_id = "test_bot_id"
    channel_id = "channel123"
    user_id = "test_user_id"

    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        turn_id = await create_turn(bot_id, channel_id, user_id)
    
        assert turn_id is not None
        assert isinstance(turn_id, str) 
        assert len(turn_id) == 36  

        mock_session.commit.assert_awaited_once()
            
@pytest.mark.asyncio
async def test_create_turn_db_failure():
    
    bot_id = "test_bot_id"
    channel_id = "channel123"
    user_id = "test_user_id"

    with mock.patch.object(DBSessionHandler, 'get_async_session', side_effect=Exception("Database error")):
        with pytest.raises(Exception):
            await create_turn(bot_id, channel_id, user_id)

@pytest.mark.asyncio
async def test_get_user_by_number_success():
    phone_number = "1234567890"
    channel_id = "channel123"
    
    mock_user = JBUser(
        id=str(uuid4()), 
        channel_id=channel_id, 
        first_name="John", 
        last_name="Doe", 
        identifier=phone_number
    )
    
    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())

    mock_execute_result = mock.Mock()
    mock_execute_result.scalars.return_value.first.return_value = mock_user 
    
    mock_session.execute = mock.AsyncMock(return_value=mock_execute_result)  

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):

        result = await get_user_by_number(phone_number, channel_id)

        assert result.id == mock_user.id
        assert result.channel_id == mock_user.channel_id
        assert result.first_name == mock_user.first_name
        assert result.last_name == mock_user.last_name
        assert result.identifier == mock_user.identifier
        mock_session.execute.assert_awaited_once() 

@pytest.mark.asyncio
async def test_get_user_by_number_failure():
    phone_number = "1234567890"
    channel_id = "channel123"
    
    with mock.patch.object(DBSessionHandler, 'get_async_session', side_effect=Exception("Database error")):
        with pytest.raises(Exception):
            await get_user_by_number(phone_number, channel_id)

@pytest.mark.asyncio
async def test_get_channel_by_id_success():
    channel_id = "channel123"
    
    mock_channel = JBChannel(
        id = channel_id,
        bot_id = "test_bot_id",
        status = "active",
        name = "telegram",
        type = "telegram",
        key = "mfvghsikzhfcdfhjsrghehssliakzjfhsk"
    )
    
    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())

    mock_execute_result = mock.Mock()
    mock_execute_result.scalars.return_value.first.return_value = mock_channel 
    
    mock_session.execute = mock.AsyncMock(return_value=mock_execute_result)  

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):

        result = await get_channel_by_id(channel_id)

        assert result.id == mock_channel.id
        assert result.bot_id == mock_channel.bot_id
        assert result.status == mock_channel.status
        assert result.name == mock_channel.name
        assert result.type == mock_channel.type
        assert result.key == mock_channel.key

        mock_session.execute.assert_awaited_once() 

@pytest.mark.asyncio
async def test_get_channel_by_id_failure():
    channel_id = "channel123"
    
    with mock.patch.object(DBSessionHandler, 'get_async_session', side_effect=Exception("Database error")):
        with pytest.raises(Exception):
            await get_channel_by_id(channel_id)

@pytest.mark.asyncio
async def test_get_bot_list_success():
    mock_bot1 = JBBot(id=1, name="Bot1", status="active")
    mock_bot2 = JBBot(id=2, name="Bot2", status="active")
    
    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_execute_result = mock.Mock()
    
    mock_scalars = mock.Mock()
    mock_scalars.unique.return_value = mock_scalars  
    mock_scalars.all.return_value = [mock_bot1, mock_bot2] 
    
    mock_execute_result.scalars.return_value = mock_scalars
    mock_session.execute = mock.AsyncMock(return_value=mock_execute_result)  

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        bot_list = await get_bot_list()
        assert bot_list == [mock_bot1, mock_bot2]
        mock_session.execute.assert_awaited_once() 


@pytest.mark.asyncio
async def test_get_bot_list_no_bots_found():

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock()) 
    mock_execute_result = mock.Mock()
    
    mock_scalars = mock.Mock()
    mock_scalars.unique.return_value = mock_scalars 
    mock_scalars.all.return_value = []
    
    mock_execute_result.scalars.return_value = mock_scalars
    mock_session.execute = mock.AsyncMock(return_value=mock_execute_result)

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        bot_list = await get_bot_list()
        assert bot_list == []
        mock_session.execute.assert_awaited_once()  

@pytest.mark.asyncio
async def test_get_channels_by_identifier_success():
    identifier = "1234567890"
    channel_type = "telegram"

    mock_channel1 = JBChannel(app_id="1234567890", type="telegram", status="inactive")
    mock_channel2 = JBChannel(app_id="1234567890", type="telegram", status="active")
    
    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_execute_result = mock.Mock()
    
    mock_scalars = mock.Mock()
    mock_scalars.unique.return_value = mock_scalars  
    mock_scalars.all.return_value = [mock_channel1, mock_channel2] 
    
    mock_execute_result.scalars.return_value = mock_scalars
    mock_session.execute = mock.AsyncMock(return_value=mock_execute_result)  

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        channels_list = await get_channels_by_identifier(identifier, channel_type) 
        assert channels_list == [mock_channel1, mock_channel2] 
        mock_session.execute.assert_awaited_once() 

@pytest.mark.asyncio
async def test_get_channels_by_identifier_no_channels_found():

    identifier = "1234567890"
    channel_type = "telegram"

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock()) 
    mock_execute_result = mock.Mock()
    
    mock_scalars = mock.Mock()
    mock_scalars.unique.return_value = mock_scalars 
    mock_scalars.all.return_value = []
    
    mock_execute_result.scalars.return_value = mock_scalars
    mock_session.execute = mock.AsyncMock(return_value=mock_execute_result)

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        channels_list = await get_channels_by_identifier(identifier, channel_type)
        assert channels_list == []
        mock_session.execute.assert_awaited_once()  

@pytest.mark.asyncio
async def test_update_bot_success():
    bot_id = "test_bot_id"
    data = {"status":"active"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 
    
    mock_execute = mock.AsyncMock() 
    mock_execute.return_value.rowcount = 1
    mock_session.execute = mock_execute

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        
        result = await update_bot(bot_id, data)
        assert result is not None
        assert result == bot_id

        mock_session.execute.assert_awaited_once() 
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_bot_no_bot_found():
    bot_id = None
    data = {"status":"active"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 

    mock_execute = mock.AsyncMock()
    mock_execute.return_value.rowcount = 0
    mock_session.execute = mock_execute 

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        result = await update_bot(bot_id, data)
        assert result is None

        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_awaited_once() 

@pytest.mark.asyncio
async def test_update_bot_error():

    bot_id = "test_bot_id"
    data = {"status":"deleted"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 
    
    mock_execute = mock.AsyncMock(side_effect=Exception("Database error"))
    mock_session.execute = mock_execute  
    
    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        with pytest.raises(Exception, match="Database error"):
            await update_bot(bot_id, data)
        
        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_not_awaited()

@pytest.mark.asyncio
async def test_update_channel_success():
    channel_id = "test_channel_id"
    data = {"status": "active", "key": "ahjbdbhsbdrhiiuciuhrqtnjuifh"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 
    
    mock_execute = mock.AsyncMock() 
    mock_execute.return_value.rowcount = 1
    mock_session.execute = mock_execute

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        result = await update_channel(channel_id, data)
        assert result is not None
        assert result == channel_id

        mock_session.execute.assert_awaited_once() 
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_channel_no_channel_found():
    channel_id = None
    data = {"status": "active", "key": "ahjbdbhsbdrhiiuciuhrqtnjuifh"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 

    mock_execute = mock.AsyncMock()
    mock_execute.return_value.rowcount = 0
    mock_session.execute = mock_execute 

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        result = await update_channel(channel_id, data)
        assert result is None

        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_awaited_once() 

@pytest.mark.asyncio
async def test_update_channel_error():
    channel_id = "test_channel_id"
    data = {"status": "active", "key": "ahjbdbhsbdrhiiuciuhrqtnjuifh"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 
    
    mock_execute = mock.AsyncMock(side_effect=Exception("Database error"))
    mock_session.execute = mock_execute  
    
    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        with pytest.raises(Exception, match="Database error"):
            await update_channel(channel_id, data)
        
        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_not_awaited()

@pytest.mark.asyncio
async def test_update_channel_by_bot_id_success():
    bot_id = "test_bot_id"
    data = {"status": "deleted"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 
    
    mock_execute = mock.AsyncMock() 
    mock_execute.return_value.rowcount = 1
    mock_session.execute = mock_execute

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        result = await update_channel_by_bot_id(bot_id, data)
        assert result is not None
        assert result == bot_id

        mock_session.execute.assert_awaited_once() 
        mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_channel_by_bot_id_no_channel_found():
    bot_id = None
    data = {"status": "deleted"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 

    mock_execute = mock.AsyncMock()
    mock_execute.return_value.rowcount = 0
    mock_session.execute = mock_execute 

    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        result = await update_channel_by_bot_id(bot_id, data)
        assert result is None

        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_awaited_once() 

@pytest.mark.asyncio
async def test_update_channel_by_bot_id_error():
    bot_id = "test_bot_id"
    data = {"status": "deleted"}

    mock_session = mock.Mock()
    mock_session.begin = mock.Mock(return_value=AsyncBeginMock())
    mock_session.commit = mock.AsyncMock() 
    
    mock_execute = mock.AsyncMock(side_effect=Exception("Database error"))
    mock_session.execute = mock_execute  
    
    with mock.patch.object(DBSessionHandler, 'get_async_session', return_value=AsyncContextManagerMock(mock_session)):
        with pytest.raises(Exception, match="Database error"):
            await update_channel_by_bot_id(bot_id, data)
        
        mock_session.execute.assert_awaited_once()
        mock_session.commit.assert_not_awaited()