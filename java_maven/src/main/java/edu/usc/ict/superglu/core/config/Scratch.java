package edu.usc.ict.superglu.core.config;

import edu.usc.ict.superglu.core.ActiveMQTopicConfiguration;
import edu.usc.ict.superglu.core.SocketIOGateway;
import edu.usc.ict.superglu.core.MessagingGateway;
import edu.usc.ict.superglu.util.SerializationConvenience;
import edu.usc.ict.superglu.util.SerializationFormatEnum;
import edu.usc.ict.superglu.vhuman.GIFTVHumanBridge;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * this is just some scratch space I made to create a quick program to build a service configuration file
 * @author auerbach
 *
 */

public class Scratch {

	public static void main(String[] args) {
		
		ActiveMQTopicConfiguration topicConfiguration = new ActiveMQTopicConfiguration("ActiveMQ", new ArrayList<>(), "tcp://localhost:61617");
		
		Map<String, Object> amqParams = new HashMap<String, Object>();
		amqParams.put(ServiceConfiguration.ACTIVEMQ_PARAM_KEY, topicConfiguration);
		
		GatewayBlackWhiteListConfiguration amqGatewayBlackList = new GatewayBlackWhiteListConfiguration();
		List<String> vhumanMessages = new ArrayList<>();
		vhumanMessages.add("VHuman.*.*");
		amqGatewayBlackList.addMessage("external", "VHuman.*.*");
		
		amqParams.put(MessagingGateway.GATEWAY_BLACKLIST_KEY, amqGatewayBlackList);
		
		String amqGatewayName = "activeMQGateway";
		String socketIOGatewayName = "socketIOGateway";
		String bridgeGatewayName = "VHMSGBridgeGateway";
		
		List<String> amqNodes = new ArrayList<>();
		
		amqNodes.add(socketIOGatewayName);
		amqNodes.add(bridgeGatewayName);
		
		ServiceConfiguration activeMQGateway = new ServiceConfiguration(amqGatewayName, ActiveMQTopicConfiguration.class, amqParams, amqNodes, new ArrayList<>(), new ArrayList<>());
		
		
		Map<String, Object> socketIOParams = new HashMap<>();
		socketIOParams.put(ServiceConfiguration.SOCKETIO_PARAM_KEY, 5333);
		
		List<String> socketIONodes = new ArrayList<>();
		socketIONodes.add(amqGatewayName);
		socketIONodes.add(bridgeGatewayName);
		
		ServiceConfiguration socketIOGateway = new ServiceConfiguration(socketIOGatewayName, SocketIOGateway.class, socketIOParams, socketIONodes, new ArrayList<>(), new ArrayList<>());
		
		
		Map<String, Object> defaultBridgeParams = new HashMap<>();
		defaultBridgeParams.put(GIFTVHumanBridge.BROKER_HOST_PARAM_KEY, "localhost");
		defaultBridgeParams.put(GIFTVHumanBridge.BROKER_PORT_PARAM_KEY, 61617);
		
		List<String> bridgeNodes = new ArrayList<>();
		bridgeNodes.add(amqGatewayName);
		bridgeNodes.add(socketIOGatewayName);
		
		ServiceConfiguration GiftVHumanBridge = new ServiceConfiguration("defaultBridge", GIFTVHumanBridge.class, defaultBridgeParams, bridgeNodes, new ArrayList<>(), new ArrayList<>());
		
		
		Map<String, ServiceConfiguration> result = new HashMap<>();
		result.put(activeMQGateway.getId(), activeMQGateway);
		result.put(socketIOGateway.getId(), socketIOGateway);
		result.put(GiftVHumanBridge.getId(), GiftVHumanBridge);

		ServiceConfigurationCollection serviceConfigs = new ServiceConfigurationCollection(result);
		String json = SerializationConvenience.serializeObject(serviceConfigs, SerializationFormatEnum.JSON_STANDARD_FORMAT);
		
		System.out.println(json);

	}

}
