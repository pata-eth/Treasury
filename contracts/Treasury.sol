pragma solidity 0.8.17;

import "./TradeHandlerHelper.sol";

contract Treasury {
    address payable public governance;
    address payable public pendingGovernance;
    bool private isOriginal = true;

    event SweptToken(address token, uint amount);
    event SweptETH(uint amount);
    event PendingGovernance(address newPendingGov);
    event AcceptedGovernance(address newGov);

    constructor(address payable _governance) public {
        _initialize(_governance);
    }

    function initialize(address payable _governance) public {
        _initialize(_governance);
    }

    function _initialize(address payable _governance) internal {
        governance = _governance;
    }

    modifier onlyGovernance() {
        require(msg.sender == governance, "!governance");
        _;
    }

    function setGovernance(address payable _newGov) external onlyGovernance {
        require(_newGov != address(0));
        pendingGovernance = _newGov;
        emit PendingGovernance(_newGov);
    }

    function acceptGovernance() external {
        require(msg.sender == pendingGovernance, "!pendingGovernance");
        governance = pendingGovernance;
        delete pendingGovernance;
        emit AcceptedGovernance(governance);
    }

    function sweep(
        address[] calldata _tokens,
        uint256[] calldata _amounts
    ) external onlyGovernance {
        uint256 _size = _tokens.length;
        require(_size == _amounts.length);

        for (uint256 i = 0; i < _size; i++) {
            if (_tokens[i] == address(0)) {
                // Native ETH
                TradeHandlerHelper.safeTransferETH(governance, _amounts[i]);
                emit SweptETH(_amounts[i]);
            } else {
                // ERC20s
                TradeHandlerHelper.safeTransfer(
                    _tokens[i],
                    governance,
                    _amounts[i]
                );
                emit SweptToken(_tokens[i], _amounts[i]);
            }
        }
    }

    event Cloned(address indexed clone);

    function clone(address payable _governance) external returns (address payable newTreasury) {
        require(isOriginal, "!original");

        bytes20 addressBytes = bytes20(address(this));

        assembly {
        // EIP-1167 bytecode
            let clone_code := mload(0x40)
            mstore(clone_code, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73000000000000000000000000)
            mstore(add(clone_code, 0x14), addressBytes)
            mstore(add(clone_code, 0x28), 0x5af43d82803e903d91602b57fd5bf30000000000000000000000000000000000)
            newTreasury := create(0, clone_code, 0x37)
        }

        Treasury(newTreasury).initialize(_governance);
        emit Cloned(newTreasury);
    }

    // `fallback` is called when msg.data is not empty
    fallback() external payable {}

    // `receive` is called when msg.data is empty
    receive() external payable {}
}
