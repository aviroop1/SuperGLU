package Core.Tests;

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import java.util.logging.ConsoleHandler;
import java.util.logging.Logger;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import Core.BaseMessagingNode;
import Core.BaseService;
import Core.Message;
import Core.MessagingGateway;
import Core.SpeechActEnum;

public class MessagingGatewayTest {

	class TestService extends BaseService
	{
		@Override
		public void receiveMessage(Message msg)
		{
			super.receiveMessage(msg);
			System.out.println("message received");
		}
		
	}
	
	private MessagingGateway gateway;
	private MessagingGateway receiver;
	
	private List<Message> testMessages;
	
	private static boolean messageConditions(Message msg)
	{
		if(msg.getActor().equals("penguin"))
			return false;
		
		return true;
	}
	
	
	@Before
	public void setUp() throws Exception {
		Predicate<Message> condition = MessagingGatewayTest::messageConditions;
		List<BaseMessagingNode> nodes = new ArrayList<>();
		Map<String, Object> scope = new HashMap<>();
		scope.put("scope1","value1");
		scope.put("key2", "penguins");
		TestService mockService = new TestService();
		nodes.add(mockService);
		
		receiver = new MessagingGateway("Receiver", null, new HashMap<>(), new ArrayList<>(), null);
		gateway = new MessagingGateway("Sender", receiver, scope, nodes, condition);
		
		mockService.bindToGateway(gateway);
		
		this.testMessages = buildMessages();
	}
	
	
	private List<Message> buildMessages()
	{
		List<Message> result = new ArrayList<>();
		
		Message msg1 = new Message("penguin", "eats", "fish", "gets fat", SpeechActEnum.INFORM_ACT, null, new HashMap<>(), "msg1");
		result.add(msg1);
		Message msg2 = new Message("TestService", "Sends Message", "to somebody", "this message should go through", SpeechActEnum.INFORM_ACT, null, new HashMap<>(), "msg2");
		result.add(msg2);
		return result;
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void testReceiveMessage() {
		for(Message msg : this.testMessages)
			gateway.receiveMessage(msg);
	}
	
	
	@Test
	public void testSendMessage()
	{
		for(Message msg : this.testMessages)
			gateway.sendMessage(msg);
	}
	

	@Test
	public void testAddContextDataToMsg() {
		Message msg1 = testMessages.get(0);
		gateway.addContextDataToMsg(msg1);
		
		Assert.assertEquals("{key2=penguins, scope1=value1}", msg1.getContext().toString());
		
		System.out.println(msg1.toString());
	}

	@Test
	public void testGetMessageConditions() {
		boolean result = gateway.getMessageConditions().test(testMessages.get(0));
		Assert.assertEquals(false, result);
		
		result = gateway.getMessageConditions().test(testMessages.get(1));
		Assert.assertEquals(true, result);
		
	}
	

	@Test
	public void testMessagesToStringListAndBack() {
		List<String> msgsAsStrings = gateway.messagesToStringList(testMessages);
		System.out.print(msgsAsStrings.toString());
		List<Message> copy = gateway.stringListToMessages(msgsAsStrings);
		
		Assert.assertEquals(testMessages, copy);
	}

}
